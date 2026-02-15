import os
import re
import time
import requests
import json
from urllib.parse import unquote, urlparse
from tqdm import tqdm

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

    def get_gofile_server(self, preferred_server=None):
        """
        Dapatkan server Gofile dengan filter server yang bermasalah
        """
        # Blacklist server yang sering bermasalah dengan file besar
        BLACKLIST = ['store-na-phx-5']  # Server yang error di log user
        
        # Jika user memilih server spesifik
        if preferred_server and preferred_server != 'auto (Singapore priority)':
            if preferred_server in BLACKLIST:
                print(f"⚠️ WARNING: {preferred_server} is known to have issues with large files")
                print(f"⚠️ Consider using auto mode or different server")
            print(f"📡 Using user-selected server: {preferred_server}")
            return preferred_server
        
        # Auto mode - cari server Singapore atau pilih yang tersedia
        try:
            req = requests.get("https://api.gofile.io/servers", timeout=10)
            data = req.json()
            
            if data['status'] == 'ok' and 'servers' in data['data']:
                servers = data['data']['servers']
                
                # Filter out blacklisted servers
                available_servers = [srv for srv in servers if srv['name'] not in BLACKLIST]
                
                if not available_servers:
                    print("⚠️ All reliable servers blacklisted, using original list")
                    available_servers = servers
                
                print(f"📡 Found {len(available_servers)} available servers:")
                
                # Tampilkan semua server
                for srv in available_servers:
                    zone = srv.get('zone', 'unknown')
                    name = srv['name']
                    status = "⚠️ " if name in BLACKLIST else "✅ "
                    print(f"   {status}{name} (Zone: {zone})")
                
                # Cari server Singapore/Asia
                for srv in available_servers:
                    zone = srv.get('zone', '').lower()
                    name = srv.get('name', '').lower()
                    if 'singapore' in zone or 'sg' in zone or 'asia' in zone or 'sg' in name:
                        print(f"🇸🇬 Selected Singapore/Asia server: {srv['name']}")
                        return srv['name']
                
                # Fallback ke server pertama yang tidak di blacklist
                server = available_servers[0]['name']
                print(f"⚠️ No Singapore server found, using: {server}")
                return server
                
        except Exception as e:
            print(f"⚠️ API fetch failed: {e}")
        
        # Ultimate fallback
        return "store1"

    def upload_to_gofile(self, filepath, server, max_retries=2):
        """
        Upload dengan retry mechanism dan better error handling
        """
        print(f"☁️ Preparing upload to Gofile")
        print(f"📁 File: {os.path.basename(filepath)}")
        print(f"🌐 Server: {server}")
        
        file_size = os.path.getsize(filepath)
        print(f"📦 Size: {self.format_size(file_size)}")
        
        # Warning untuk file besar
        if file_size > 5 * 1024 * 1024 * 1024:  # > 5GB
            print(f"⚠️ WARNING: Large file detected ({self.format_size(file_size)})")
            print(f"⚠️ Upload may take a long time or fail. Consider:")
            print(f"   - Splitting the file")
            print(f"   - Using a more stable server")
            print(f"   - Uploading during off-peak hours")
        
        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                print(f"\n🔄 Retry attempt {attempt}/{max_retries}")
                time.sleep(5)  # Wait before retry
            
            try:
                upload_url = f"https://{server}.gofile.io/uploadFile"
                
                print(f"\n📤 Uploading to {upload_url}...")
                start_time = time.time()
                
                with open(filepath, 'rb') as f:
                    # Timeout yang lebih besar untuk file besar (1 hour + 10 seconds per MB)
                    timeout_seconds = 3600 + (file_size / (1024 * 1024)) * 10
                    
                    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Uploading") as pbar:
                        files = {'file': (os.path.basename(filepath), f)}
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        
                        # Upload dengan timeout yang sesuai
                        response = requests.post(
                            upload_url, 
                            files=files, 
                            headers=headers,
                            timeout=timeout_seconds
                        )
                
                elapsed = time.time() - start_time
                print(f"⏱️ Upload took: {elapsed:.1f} seconds")
                
                # Debug: Print raw response
                print(f"📋 Response status: {response.status_code}")
                print(f"📋 Response headers: {dict(response.headers)}")
                
                # Parse response dengan error handling
                try:
                    result = response.json()
                    print(f"📋 Response JSON: {json.dumps(result, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON response")
                    print(f"📋 Raw response (first 500 chars):")
                    print(response.text[:500])
                    
                    # Save raw response for debugging
                    with open('gofile_error_response.txt', 'w') as f:
                        f.write(f"Status Code: {response.status_code}\n")
                        f.write(f"Headers: {response.headers}\n\n")
                        f.write(f"Body:\n{response.text}")
                    print(f"💾 Full response saved to: gofile_error_response.txt")
                    
                    if attempt < max_retries:
                        continue
                    else:
                        return None
                
                # Check if upload was successful
                if result.get('status') == 'ok' and 'data' in result:
                    data = result['data']
                    
                    # Validate required fields
                    if 'downloadPage' not in data:
                        print(f"❌ Response missing 'downloadPage' field")
                        if attempt < max_retries:
                            continue
                        else:
                            return None
                    
                    download_link = data['downloadPage']
                    file_id = data.get('fileId', 'N/A')
                    
                    print(f"\n🎉 Upload SUCCESS!")
                    print(f"🔗 Download Link: {download_link}")
                    print(f"📄 File ID: {file_id}")
                    
                    # Simpan hasil ke file untuk GitHub Actions
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
                    error_msg = result.get('message', result.get('error', 'Unknown error'))
                    print(f"\n❌ Upload failed: {error_msg}")
                    print(f"📋 Full response: {result}")
                    
                    if attempt < max_retries:
                        print(f"🔄 Will retry with same or different server...")
                    else:
                        with open('gofile_result.txt', 'w') as f:
                            f.write(f"❌ Upload Failed\n")
                            f.write(f"Error: {error_msg}\n")
                            f.write(f"Full response: {json.dumps(result, indent=2)}\n")
                
            except requests.exceptions.Timeout as e:
                print(f"\n❌ Upload timeout after {timeout_seconds}s: {e}")
                if attempt < max_retries:
                    print(f"🔄 Will retry...")
                else:
                    with open('gofile_result.txt', 'w') as f:
                        f.write(f"❌ Upload Timeout\n")
                        f.write(f"Error: {str(e)}\n")
                
            except Exception as e:
                print(f"\n❌ Upload error: {e}")
                print(f"Error type: {type(e).__name__}")
                
                if attempt < max_retries:
                    print(f"🔄 Will retry...")
                else:
                    with open('gofile_result.txt', 'w') as f:
                        f.write(f"❌ Upload Error\n")
                        f.write(f"Error: {str(e)}\n")
                        f.write(f"Error type: {type(e).__name__}\n")
        
        return None

    def process(self, url, preferred_server=None, keep_file=False):
        print("="*60)
        print("🤖 Gofile Mirror Bot - Enhanced Version")
        print("="*60)
        print(f"\n🎯 Processing URL: {url}")
        
        # Parse URL (handle SourceForge)
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
            # Get server
            server = self.get_gofile_server(preferred_server)
            print()
            
            # Upload dengan retry
            result = self.upload_to_gofile(filepath, server, max_retries=2)
            
            # Cleanup - HANYA hapus jika upload SUKSES
            if result:  # Upload sukses
                if not keep_file:
                    try:
                        os.remove(filepath)
                        print(f"\n🗑️ Local file deleted: {filename}")
                    except Exception as e:
                        print(f"\n⚠️ Failed to delete file: {e}")
                else:
                    print(f"\n💾 Local file kept: {filepath}")
            else:  # Upload gagal
                print(f"\n💾 Upload failed - Local file PRESERVED: {filepath}")
                print(f"💡 You can try uploading manually or retry later")
            
            return result
        else:
            print("\n❌ Download failed, aborting upload")
            with open('gofile_result.txt', 'w') as f:
                f.write(f"❌ Download Failed\n")
                f.write(f"URL: {url}\n")
            return None

if __name__ == "__main__":
    # Baca environment variables dari GitHub Actions
    download_url = os.getenv('DOWNLOAD_URL')
    gofile_server = os.getenv('GOFILE_SERVER', 'auto (Singapore priority)')
    keep_local = os.getenv('KEEP_LOCAL_FILE', 'false').lower() == 'true'
    
    if not download_url:
        print("❌ Error: DOWNLOAD_URL environment variable not set")
        exit(1)
    
    # Jalankan bot
    bot = GofileMirrorBot()
    result = bot.process(download_url, gofile_server, keep_file=keep_local)
    
    # Exit code untuk GitHub Actions
    exit(0 if result else 1)
