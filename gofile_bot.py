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
            response = self.session.get(url, stream=True, allow_redirects=True)
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
        Dapatkan server Gofile
        Args:
            preferred_server: 'auto', 'store1', 'store2', etc.
        """
        # Jika user memilih server spesifik
        if preferred_server and preferred_server != 'auto (Singapore priority)':
            print(f"📡 Using user-selected server: {preferred_server}")
            return preferred_server
        
        # Auto mode - cari server Singapore atau pilih yang tersedia
        try:
            req = requests.get("https://api.gofile.io/servers", timeout=5)
            data = req.json()
            
            if data['status'] == 'ok' and 'servers' in data['data']:
                servers = data['data']['servers']
                print(f"📡 Found {len(servers)} available servers")
                
                # Tampilkan semua server
                for srv in servers:
                    zone = srv.get('zone', 'unknown')
                    print(f"   - {srv['name']} (Zone: {zone})")
                
                # Cari server Singapore/Asia
                for srv in servers:
                    zone = srv.get('zone', '').lower()
                    name = srv.get('name', '').lower()
                    if 'singapore' in zone or 'sg' in zone or 'asia' in zone or 'sg' in name:
                        print(f"🇸🇬 Selected Singapore/Asia server: {srv['name']}")
                        return srv['name']
                
                # Fallback ke server pertama
                server = servers[0]['name']
                print(f"⚠️ No Singapore server found, using: {server}")
                return server
                
        except Exception as e:
            print(f"⚠️ API fetch failed: {e}")
        
        # Ultimate fallback
        return "store1"

    def upload_to_gofile(self, filepath, server):
        print(f"☁️ Preparing upload to Gofile")
        print(f"📁 File: {os.path.basename(filepath)}")
        print(f"🌐 Server: {server}")
        
        try:
            upload_url = f"https://{server}.gofile.io/uploadFile"
            file_size = os.path.getsize(filepath)
            
            with open(filepath, 'rb') as f:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc="Uploading") as pbar:
                    # Untuk monitoring progress
                    files = {'file': (os.path.basename(filepath), f)}
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    
                    response = requests.post(upload_url, files=files, headers=headers)
            
            result = response.json()
            
            if result['status'] == 'ok':
                download_link = result['data']['downloadPage']
                file_id = result['data']['fileId']
                
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
                
                return download_link
            else:
                error_msg = result.get('message', 'Unknown error')
                print(f"\n❌ Upload failed: {error_msg}")
                
                with open('gofile_result.txt', 'w') as f:
                    f.write(f"❌ Upload Failed\n")
                    f.write(f"Error: {error_msg}\n")
                
                return None
                
        except Exception as e:
            print(f"\n❌ Upload error: {e}")
            
            with open('gofile_result.txt', 'w') as f:
                f.write(f"❌ Upload Error\n")
                f.write(f"Error: {str(e)}\n")
            
            return None

    def process(self, url, preferred_server=None):
        print("="*60)
        print("🤖 Gofile Mirror Bot - GitHub Actions")
        print("="*60)
        print(f"\n🎯 Processing URL: {url}")
        
        # Parse URL (handle SourceForge)
        direct_url = self.parse_sourceforge_url(url)
        
        # Get filename
        try:
            head = self.session.head(direct_url, allow_redirects=True)
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
            
            # Upload
            result = self.upload_to_gofile(filepath, server)
            
            # Cleanup - HAPUS FILE
            try:
                os.remove(filepath)
                print(f"\n🗑️ Local file deleted: {filename}")
            except Exception as e:
                print(f"\n⚠️ Failed to delete file: {e}")
            
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
    
    if not download_url:
        print("❌ Error: DOWNLOAD_URL environment variable not set")
        exit(1)
    
    # Jalankan bot
    bot = GofileMirrorBot()
    bot.process(download_url, gofile_server)
