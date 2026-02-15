import os
import re
import time
import requests
import json
from urllib.parse import unquote, urlparse
from tqdm import tqdm
import concurrent.futures

class GofileMirrorBot:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        })
        self.download_path = "./downloads/"
        self.setup_environment()

    def setup_environment(self):
        os.makedirs(self.download_path, exist_ok=True)

    def format_size(self, bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

    def parse_sourceforge_url(self, url):
        if 'sourceforge.net' not in url:
            return url
        try:
            project_match = re.search(r'projects/([^/]*)/files', url)
            filepath_match = re.search(r'files/(.*?)(?:/download|$)', url)
            if project_match and filepath_match:
                return f"https://master.dl.sourceforge.net/project/{project_match.group(1)}/{filepath_match.group(1)}?viasf=1"
        except:
            pass
        return url

    def get_filename_from_url(self, url, response=None):
        filename = None
        if response and 'content-disposition' in response.headers:
            cd = response.headers['content-disposition']
            fname = re.search(r'filename[*]?=([^;]+)', cd)
            if fname:
                filename = unquote(fname.group(1).strip('"\''))
        
        if not filename:
            path = urlparse(url).path
            filename = os.path.basename(path)
        
        return filename or 'downloaded_file'

    def download_file(self, url, filename):
        print(f"🚀 Starting download: {filename}")
        try:
            response = self.session.get(url, stream=True, allow_redirects=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            if total_size:
                print(f"📦 File size: {self.format_size(total_size)}")

            filepath = os.path.join(self.download_path, filename)
            
            with open(filepath, 'wb') as f:
                if total_size:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                        for chunk in response.iter_content(chunk_size=65536):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
            
            print(f"✅ Download completed: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None

    def ping_server(self, server_name, timeout=5):
        """
        Test response time dari server Gofile
        Returns: (server_name, response_time_ms, success)
        """
        try:
            test_url = f"https://{server_name}.gofile.io/uploadFile"
            start = time.time()
            
            # HEAD request untuk test connectivity tanpa upload
            response = requests.head(test_url, timeout=timeout)
            
            elapsed = (time.time() - start) * 1000  # Convert to milliseconds
            
            # Check jika server respond dengan status yang valid
            if response.status_code in [200, 405, 404]:  # 405 OK (method not allowed), 404 OK (endpoint moved)
                return (server_name, elapsed, True)
            else:
                return (server_name, float('inf'), False)
                
        except requests.exceptions.Timeout:
            return (server_name, float('inf'), False)
        except Exception as e:
            return (server_name, float('inf'), False)

    def get_fastest_server(self, preferred_server=None, test_all=True):
        """
        Ping semua server dan pilih yang tercepat
        
        Args:
            preferred_server: Jika diset, langsung return ini (user override)
            test_all: Jika False, hanya test 3 server tercepat
        """
        # Blacklist server yang diketahui bermasalah
        BLACKLIST = ['store-na-phx-5']
        
        # Jika user pilih server spesifik, respect pilihan mereka
        if preferred_server and preferred_server not in ['auto', 'auto (Singapore priority)', 'fastest']:
            if preferred_server in BLACKLIST:
                print(f"⚠️ WARNING: {preferred_server} is blacklisted (known issues)")
                print(f"⚠️ Continuing anyway as per your request...")
            print(f"📡 Using user-selected server: {preferred_server}")
            return preferred_server
        
        print(f"🔍 Finding fastest Gofile server...")
        
        # Ambil list server dari API
        try:
            req = requests.get("https://api.gofile.io/servers", timeout=10)
            data = req.json()
            
            if data['status'] != 'ok' or 'servers' not in data['data']:
                print(f"⚠️ API call failed, using fallback server")
                return "store1"
            
            servers = data['data']['servers']
            
            # Filter blacklisted servers
            available_servers = [srv for srv in servers if srv['name'] not in BLACKLIST]
            
            if not available_servers:
                print(f"⚠️ All servers blacklisted, using original list")
                available_servers = servers
            
            print(f"📡 Found {len(available_servers)} available servers")
            
            # Ping semua server secara parallel
            server_speeds = []
            
            print(f"⚡ Testing server speeds...")
            
            # Gunakan ThreadPoolExecutor untuk ping parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Submit ping tasks
                future_to_server = {
                    executor.submit(self.ping_server, srv['name']): srv 
                    for srv in available_servers
                }
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_server):
                    server_info = future_to_server[future]
                    try:
                        server_name, response_time, success = future.result()
                        zone = server_info.get('zone', 'unknown')
                        
                        if success:
                            server_speeds.append({
                                'name': server_name,
                                'zone': zone,
                                'ping': response_time,
                                'success': True
                            })
                            # Print real-time result
                            print(f"   ✅ {server_name:20s} | {zone:15s} | {response_time:6.0f}ms")
                        else:
                            print(f"   ❌ {server_name:20s} | {zone:15s} | Timeout/Failed")
                            
                    except Exception as e:
                        print(f"   ❌ {server_info['name']:20s} | Error: {e}")
            
            # Sort by ping (ascending)
            server_speeds.sort(key=lambda x: x['ping'])
            
            if not server_speeds:
                print(f"⚠️ No servers responded, using fallback")
                return "store1"
            
            # Pilih server tercepat
            fastest = server_speeds[0]
            
            print(f"\n🏆 FASTEST SERVER SELECTED:")
            print(f"   Server: {fastest['name']}")
            print(f"   Zone: {fastest['zone']}")
            print(f"   Ping: {fastest['ping']:.0f}ms")
            
            # Show top 3 alternatives
            if len(server_speeds) > 1:
                print(f"\n📊 Top 3 Servers:")
                for i, srv in enumerate(server_speeds[:3], 1):
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                    print(f"   {emoji} {srv['name']:20s} | {srv['zone']:15s} | {srv['ping']:6.0f}ms")
            
            return fastest['name']
            
        except Exception as e:
            print(f"⚠️ Server speed test failed: {e}")
            print(f"⚠️ Using fallback server: store1")
            return "store1"

    def upload_to_gofile(self, filepath, server, max_retries=2):
        """Upload dengan retry mechanism dan better error handling"""
        print(f"\n☁️ Preparing upload to Gofile")
        print(f"📁 File: {os.path.basename(filepath)}")
        print(f"🌐 Server: {server}")
        
        file_size = os.path.getsize(filepath)
        print(f"📦 Size: {self.format_size(file_size)}")
        
        # Warning untuk file besar
        if file_size > 5 * 1024 * 1024 * 1024:
            print(f"⚠️ Large file warning ({self.format_size(file_size)})")
            print(f"   Upload may take long time")
        
        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                print(f"\n🔄 Retry {attempt}/{max_retries}")
                time.sleep(5)
            
            try:
                upload_url = f"https://{server}.gofile.io/uploadFile"
                start_time = time.time()
                
                print(f"\n📤 Uploading to {upload_url}...")
                
                with open(filepath, 'rb') as f:
                    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Uploading") as pbar:
                        files = {'file': (os.path.basename(filepath), f)}
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        
                        # Timeout: 1 jam + 10 detik per MB
                        timeout = 3600 + (file_size / (1024 * 1024)) * 10
                        
                        response = requests.post(
                            upload_url, 
                            files=files, 
                            headers=headers,
                            timeout=timeout
                        )
                
                elapsed = time.time() - start_time
                print(f"\n⏱️ Upload took: {elapsed:.1f} seconds")
                
                # Parse response
                try:
                    result = response.json()
                    
                    if result.get('status') == 'ok' and 'data' in result:
                        data = result['data']
                        
                        if 'downloadPage' not in data:
                            print(f"❌ Response missing 'downloadPage' field")
                            if attempt < max_retries:
                                continue
                            return None
                        
                        download_link = data['downloadPage']
                        file_id = data.get('fileId', 'N/A')
                        
                        print(f"\n🎉 Upload SUCCESS!")
                        print(f"🔗 Download Link: {download_link}")
                        print(f"📄 File ID: {file_id}")
                        
                        # Save result
                        with open('gofile_result.txt', 'w') as f:
                            f.write(f"✅ Upload Successful!\n")
                            f.write(f"📁 File: {os.path.basename(filepath)}\n")
                            f.write(f"📦 Size: {self.format_size(file_size)}\n")
                            f.write(f"🌐 Server: {server}\n")
                            f.write(f"🔗 Link: {download_link}\n")
                            f.write(f"📄 File ID: {file_id}\n")
                            f.write(f"⏱️ Upload time: {elapsed:.1f}s\n")
                        
                        return download_link
                    else:
                        error = result.get('message', result.get('error', 'Unknown error'))
                        print(f"\n❌ Upload failed: {error}")
                        
                        if attempt < max_retries:
                            print(f"🔄 Will retry...")
                        
                except json.JSONDecodeError:
                    print(f"\n❌ Invalid JSON response")
                    print(f"📋 Response status: {response.status_code}")
                    print(f"📋 First 500 chars: {response.text[:500]}")
                    
                    # Save error
                    with open('gofile_error_response.txt', 'w') as f:
                        f.write(f"Status: {response.status_code}\n")
                        f.write(f"Headers: {dict(response.headers)}\n\n")
                        f.write(f"Body:\n{response.text}")
                    
                    if attempt < max_retries:
                        continue
                
            except requests.exceptions.Timeout:
                print(f"\n❌ Upload timeout")
                if attempt < max_retries:
                    print(f"🔄 Retrying...")
                    
            except Exception as e:
                print(f"\n❌ Upload error: {e} ({type(e).__name__})")
                if attempt < max_retries:
                    print(f"🔄 Retrying...")
        
        return None

    def process(self, url, preferred_server=None, keep_file=False):
        print("="*60)
        print("🤖 Gofile Mirror Bot - Smart Server Selection")
        print("="*60)
        print(f"\n🎯 Processing URL: {url}")
        
        # Parse URL
        direct_url = self.parse_sourceforge_url(url)
        
        # Get filename
        try:
            head = self.session.head(direct_url, allow_redirects=True, timeout=10)
            filename = self.get_filename_from_url(direct_url, head)
        except:
            filename = self.get_filename_from_url(direct_url)
        
        print(f"📝 Filename: {filename}\n")
        
        # Download
        filepath = self.download_file(direct_url, filename)
        
        if filepath and os.path.exists(filepath):
            print()
            
            # Get fastest server
            server = self.get_fastest_server(preferred_server)
            print()
            
            # Upload dengan retry
            result = self.upload_to_gofile(filepath, server, max_retries=2)
            
            # Cleanup - HANYA hapus jika upload SUKSES
            if result:
                if not keep_file:
                    try:
                        os.remove(filepath)
                        print(f"\n🗑️ Local file deleted: {filename}")
                    except Exception as e:
                        print(f"\n⚠️ Failed to delete file: {e}")
                else:
                    print(f"\n💾 Local file kept: {filepath}")
            else:
                print(f"\n💾 Upload failed - Local file PRESERVED: {filepath}")
                print(f"💡 You can retry later without re-downloading")
            
            return result
        else:
            print("\n❌ Download failed, aborting")
            return None

if __name__ == "__main__":
    # Baca environment variables
    download_url = os.getenv('DOWNLOAD_URL')
    gofile_server = os.getenv('GOFILE_SERVER', 'fastest')
    keep_local = os.getenv('KEEP_LOCAL_FILE', 'false').lower() == 'true'
    
    if not download_url:
        print("❌ Error: DOWNLOAD_URL not set")
        exit(1)
    
    # Jalankan bot
    bot = GofileMirrorBot()
    result = bot.process(download_url, gofile_server, keep_file=keep_local)
    
    exit(0 if result else 1)
