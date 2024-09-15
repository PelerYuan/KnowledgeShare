# 使用官方的Python基础镜像
FROM python

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 暴露应用的端口
EXPOSE 8000

# 启动Django开发服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
