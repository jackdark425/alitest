# Serverless Devs 开发指南

> 阿里云函数计算（FC）开发最佳实践和快速入门指南

## 目录

- [环境准备](#环境准备)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [配置文件说明](#配置文件说明)
- [函数模板](#函数模板)
- [开发调试](#开发调试)
- [高阶用法](#高阶用法)
- [最佳实践](#最佳实践)
- [常用命令](#常用命令)

## 环境准备

### 1. 安装 Serverless Devs 工具
```bash
# 安装命令行工具
npm install @serverless-devs/s -g

# 验证安装
s -v

# 配置阿里云密钥
s config add
```

### 2. 密钥配置说明
- 在阿里云 RAM 访问控制创建子账号
- 获取 AccessKey ID 和 AccessKey Secret
- 使用 `s config add` 配置密钥信息

## 快速开始

### 1. 初始化项目
```bash
# Node.js HTTP 函数
s init start-fc3-nodejs-http

# Python 函数
s init start-fc3-python -d my-python-app

# 更多函数模板
s init devsapp/start-fc3
```

### 2. 开发部署
```bash
# 进入项目目录
cd my-function

# 安装依赖
npm install  # Node.js
pip install -r requirements.txt -t ./code/python  # Python

# 部署函数
s deploy

# 调用测试
s invoke -e "test"
```

## 项目结构

```
project/
  ├── s.yaml              # Serverless 配置文件
  └── code/              
      ├── index.js/py     # 函数入口文件
      ├── package.json    # (Node.js) 依赖配置
      └── requirements.txt # (Python) 依赖配置
```

## 配置文件说明

### s.yaml 基础配置
```yaml
edition: 3.0.0
name: app-name
access: "default"

vars: # 全局变量
  region: "cn-beijing"

resources:
  hello_world:
    component: fc3 
    props:
      region: ${vars.region}              
      functionName: "function-name"
      description: 'function description'
      runtime: "nodejs16/python3.10"
      code: ./code
      handler: "index.handler"
      memorySize: 128
      timeout: 30
      
      # 环境变量配置
      environmentVariables:
        PYTHONPATH: /code/python # Python依赖路径
        NODE_ENV: production
      
      # HTTP触发器配置
      triggers:
        - triggerName: httpTrigger
          triggerType: http
          triggerConfig:
            authType: anonymous
            methods: 
              - GET
              - POST
```

## 函数模板

### Node.js HTTP 函数
```javascript
'use strict';
exports.handler = async (event, context) => {
  try {
    const eventObj = JSON.parse(event);
    console.log('收到事件:', JSON.stringify(eventObj));
    
    // 处理请求数据
    let requestBody = '';
    if (eventObj.body) {
      requestBody = eventObj.isBase64Encoded 
        ? Buffer.from(eventObj.body, 'base64').toString()
        : eventObj.body;
    }
    
    // 业务逻辑处理
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'success',
        data: {}
      })
    };
  } catch (error) {
    console.error('错误:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: 'error',
        error: error.message
      })
    };
  }
};
```

### Python 函数
```python
# -*- coding: utf-8 -*-
import json
import logging

logger = logging.getLogger()

def handler(event, context):
    try:
        # 设置日志级别
        logger.setLevel(logging.INFO)
        
        # 记录事件信息
        logger.info('收到事件: %s', event)
        
        # 解析事件数据
        evt = json.loads(event)
        
        # 业务逻辑处理
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'success',
                'data': {}
            })
        }
    except Exception as e:
        logger.error('错误: %s', str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'error',
                'error': str(e)
            })
        }
```

## 开发调试

### 本地调试
```bash
# 本地启动函数
s local start

# 本地调用测试
s local invoke -e "event data"

# 实时日志调试
s local invoke -e "event data" --debug

# 监听文件变化
s local start --watch
```

### 依赖安装

#### Python 项目
```bash
pip install -r requirements.txt -t ./code/python
```

#### Node.js 项目
```bash
cd code
npm install
```

### 开发调试技巧
```bash
# 使用 custom 命令调用
s cli fc3 invoke --service-name xxx --function-name xxx

# 环境隔离开发
s deploy --use-local --skip-push

# 并发压测
s cli fc3 invoke --concurrency 10
```

## 高阶用法

### 1. 环境变量配置
```yaml
props:
  environmentVariables:
    MYSQL_HOST: xxx.mysql.com
    REDIS_URL: xxx.redis.com
    API_KEY: ${secret(API_KEY)}  # 从密钥管理服务获取
```

### 2. 自定义域名
```yaml
props:
  customDomains:
    - domainName: auto
      protocol: HTTP
      routeConfigs:
        - path: /*
          serviceName: html
```

### 3. VPC 配置
```yaml
props:
  vpcConfig:
    vpcId: vpc-xxx
    securityGroupId: sg-xxx
    vswitchIds:
      - vsw-xxx
```

### 4. 弹性伸缩
```yaml
props:
  instanceConcurrency: 20
  instanceLifecycleConfig:
    preFreeze:
      handler: index.preFreeze
      timeout: 3
```

### 5. 分层部署
```yaml
props:
  layers:
    - name: common-layer
      version: 1
```

## 最佳实践

### 1. 冷启动优化
```javascript
// 全局变量复用
const db = {}
exports.handler = async (event) => {
  if (!db.connection) {
    db.connection = await createConnection()
  }
}
```

### 2. 日志规范
```python
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)

def handler(event, context):
    logging.info('Request: %s', event)
    try:
        # 业务逻辑
        pass
    except Exception as e:
        logging.error('Error: %s', str(e))
        raise
```

### 3. 监控配置
```yaml
props:
  monitors:
    - name: errorRate
      threshold: 1
      period: 300
      evaluationCount: 3
      statistics: Average
      comparisonOperator: GreaterThanThreshold
```

## 常用命令

### 基础命令
```bash
s deploy              # 部署应用
s remove              # 移除应用
s info                # 查看信息
s logs                # 查看日志
s metrics             # 查看指标
s build               # 构建应用
```

### 开发命令
```bash
s local start         # 本地调试
s invoke              # 触发函数
s local invoke        # 本地触发
s logs --tail         # 实时日志
```

### 版本管理
```bash
s version             # 发布版本
s alias              # 管理别名
```

### 测试命令
```bash
s test unit          # 单元测试
s test integration   # 集成测试
s test stress -c 100 -n 1000  # 压力测试
```

## 参考资料

- [官方手册](https://manual.serverless-devs.com/user-guide/aliyun/#fc3)
- [使用案例](https://manual.serverless-devs.com/user-guide/tips/)
- [效率提升最佳实践](https://manual.serverless-devs.com/practices/efficiency/)