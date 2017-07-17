from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = 'n_zDMmovafNwwBKr2UgED88ETSlk7rpgJwoWA8sP'
secret_key = 'B4pTA3T_UHo6-sfDc6R0lD7_HLF7IlMmeWSzpbHR'
#构建鉴权对象
q = Auth(access_key, secret_key)
#要上传的空间
bucket_name = 'lichi'
#上传到七牛后保存的文件名

#生成上传 Token，可以指定过期时间等
token = q.upload_token(bucket_name)
#要上传文件的本地路径
print(token)
# localfile = 'C:\\Users\\Cloud\Desktop\\wallhaven-463196.jpg'
# ret, info = put_file(token, key, localfile)
# print(info)
# assert ret['key'] == key
# assert ret['hash'] == etag(localfile)