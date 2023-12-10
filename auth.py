import requests 
import io
import json
import os
import time
from dotenv import load_dotenv # 用来加载环境变量
from requests_toolbelt import MultipartEncoder

# 从环境变量中获取 APP_ID 和 APP_SECRET
load_dotenv()  # 加载 .env 文件中的环境变量
APP_ID = os.environ.get('APP_ID')
APP_SECRET = os.environ.get('APP_SECRET')
PARENT_NODE = os.environ.get('PARENT_NODE')
BASE_APP_TOKEN = os.environ.get('BASE_APP_TOKEN')
BASE_TABLE_ID = os.environ.get('BASE_TABLE_ID')


# 获取 tenant_access_token ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
def get_tenant_access_token(): 
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" # 生成 tenant_access_token 的接口
    headers = {
		"Content-Type": "application/json"
	}
    payload = {
		"app_id": APP_ID,
		"app_secret": APP_SECRET
	}
    
    # 发送请求
    response = requests.post(url=url, headers=headers, json=payload)
    response_data = response.json()
    print("🔑 获得了 tenant_access_token: \n", response_data.get("tenant_access_token"), "\n")
    return response_data.get("tenant_access_token") # 返回 tenant_access_token
    

 
# 上传到文件夹 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# 从获得的 tenant_access_token 来上传图片 https://open.feishu.cn/open-apis/drive/v1/files/upload_all
def upload_file_toBase(file_name, full_imageFile_path, tenant_access_token):
    file_size = os.path.getsize(full_imageFile_path) # 获取文件大小
    # url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" # 上传接口 => 上传到文件夹, 文件夹内可见
    url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all" # 上传接口 => 上传到文件夹, 且文件夹内不可见
   
    headers = { #🔥 需要先定义 header 才能在下方去更嗨 header 的 Content-Type !!
		"Authorization": "Bearer " + tenant_access_token,
	}
   # 👇提交到文件夹内 ___ 
    # # 以表单形式提交数据
    # form = {'file_name': file_name,
    #         'parent_type': 'explorer',
    #         'parent_node': BASE_APP_TOKEN, # 🔥上传到多维表格内!!
    #         'size': str(file_size),
    #         'file': (open(full_imageFile_path, 'rb'))}  
    # multi_form = MultipartEncoder(form)
    
    # headers['Content-Type'] = multi_form.content_type
    
    # 👇提交到多维表格内
	# 以表单形式提交数据
    form = {'file_name': file_name,
            'parent_type': 'bitable_image',
            'parent_node': BASE_APP_TOKEN, # 🔥上传到多维表格内!!
            'size': str(file_size),
            'file': (open(full_imageFile_path, 'rb'))}  
    multi_form = MultipartEncoder(form)
    
    # 验证 token + 设置 Content-Type
    headers['Content-Type'] = multi_form.content_type
    
   
    print("📤 开始上传文件...")
    response = requests.request("POST", url, headers=headers, data=multi_form)
    
    if response.status_code == 200:
        response_data = response.json()
		# 返回 file_token

		# return response_data
        file_token = response_data['data']['file_token']  # 提取 file_token
        print("📤 上传 base 文件成功, file_token 为: \n", file_token, "\n")
        return file_token
		
		# file_token = response_data["file_token"]
		# print(file_token)
    else:
        print("❌ 新增 base 记录失败", response.status_code)
        return "404"
    
    
# 新增一条 base 记录
def add_base_record(file_name, file_token, tenant_access_token):
    app_token = BASE_APP_TOKEN
    table_id = BASE_TABLE_ID
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records" # 新增 record 接口
    
	# 添加 app_id 跟 app_secret
    headers = {
		"Authorization": "Bearer " + tenant_access_token,
	}
    
    # 构建请求体的字典
    request_body = {
		"fields": {
			"name": file_name, # 🔥 生图后获得
			"file": [{
			"file_token": file_token # 🔥 上传到云文档后获得
			}]
		}
	}
    
	# 将字典转换为 JSON 格式的字符串
    # json_request_body = json.dumps(request_body)
    
	# 发送请求
    response = requests.post(url=url, headers=headers, json=request_body)
    print("📤 开始新增 base 记录...")
    
    if response.status_code == 200:
        response_data = response.json()
        print("📤 新增 base 记录成功: \n", response_data, "\n")
        return response_data
    else:
        print("❌ 新增 base 记录失败", response.status_code)
        return "404"
    
    
    

