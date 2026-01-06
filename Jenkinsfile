pipeline {
    agent any

    options {
        // 构建超时设置（2小时）
        timeout(time: 2, unit: 'HOURS')
        // 保留最近10次构建
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // 禁用并发构建
        disableConcurrentBuilds()
        // 添加时间戳
        timestamps()
    }

    environment {
        // Python 虚拟环境路径
        PYTHON_ENV = "${WORKSPACE}/venv"
        // 测试环境变量（可通过 Jenkins 参数覆盖）
        TEST_ENV = "${params.TEST_ENV ?: 'test'}"
        // 测试标记（可通过 Jenkins 参数覆盖）
        TEST_MARKERS = "${params.TEST_MARKERS ?: ''}"
        // 并行 worker 数量
        PARALLEL_WORKERS = "${params.PARALLEL_WORKERS ?: 'auto'}"
        // Allure 结果目录
        ALLURE_RESULTS_DIR = "report/allure-results"
        // 报告目录
        REPORT_DIR = "report"
    }

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['dev', 'test', 'staging', 'prod'],
            description: '选择测试环境'
        )
        choice(
            name: 'TEST_TYPE',
            choices: ['all', 'ui', 'api', 'smoke', 'regression'],
            description: '选择测试类型'
        )
        string(
            name: 'TEST_MARKERS',
            defaultValue: '',
            description: '自定义测试标记（如：ui and smoke）'
        )
        choice(
            name: 'PARALLEL_WORKERS',
            choices: ['auto', '1', '2', '4', '8'],
            description: '并行执行 worker 数量'
        )
        booleanParam(
            name: 'INSTALL_BROWSERS',
            defaultValue: true,
            description: '是否安装 Playwright 浏览器'
        )
        booleanParam(
            name: 'CLEAN_WORKSPACE',
            defaultValue: true,
            description: '构建后是否清理工作空间'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "开始拉取代码..."
                    echo "分支: ${env.BRANCH_NAME ?: 'main'}"
                }
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    echo "设置 Python 环境..."
                    echo "Python 版本: ${sh(script: 'python3 --version', returnStdout: true).trim()}"
                }
                sh '''
                    # 创建虚拟环境（如果不存在）
                    if [ ! -d "${PYTHON_ENV}" ]; then
                        python3 -m venv ${PYTHON_ENV}
                    fi

                    # 激活虚拟环境并升级 pip
                    . ${PYTHON_ENV}/bin/activate
                    pip install --upgrade pip setuptools wheel

                    # 安装项目依赖
                    pip install -r requirements.txt

                    # 显示已安装的包
                    pip list
                '''
            }
        }

        stage('Install Playwright Browsers') {
            when {
                anyOf {
                    params.INSTALL_BROWSERS == true
                    expression { params.TEST_TYPE == 'all' || params.TEST_TYPE == 'ui' }
                }
            }
            steps {
                script {
                    echo "安装 Playwright 浏览器驱动..."
                }
                sh '''
                    . ${PYTHON_ENV}/bin/activate
                    # 安装 Playwright 浏览器（仅安装 chromium 以节省时间）
                    playwright install chromium
                    # 如果需要安装所有浏览器，取消下面的注释
                    # playwright install --with-deps
                '''
            }
        }

        stage('Create Directories') {
            steps {
                sh '''
                    # 创建必要的目录
                    mkdir -p ${REPORT_DIR}/allure-results
                    mkdir -p ${REPORT_DIR}/allure-report
                    mkdir -p logs
                    mkdir -p screenshots
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def testCommand = buildTestCommand()
                    echo "执行测试命令: ${testCommand}"
                    
                    sh """
                        . ${PYTHON_ENV}/bin/activate
                        export TEST_ENV=${TEST_ENV}
                        ${testCommand}
                    """
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                script {
                    echo "生成 Allure 报告..."
                }
                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: "${ALLURE_RESULTS_DIR}"]]
                ])
            }
        }

        stage('Archive Test Results') {
            steps {
                script {
                    echo "归档测试结果..."
                }
                archiveArtifacts artifacts: 'logs/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: 'screenshots/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: "${ALLURE_RESULTS_DIR}/**/*", allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            script {
                echo "构建完成，清理环境..."
                
                // 发布测试结果摘要
                def testResults = sh(
                    script: ". ${PYTHON_ENV}/bin/activate && pytest --collect-only -q 2>/dev/null | tail -1 || echo 'No tests found'",
                    returnStdout: true
                ).trim()
                echo "测试结果摘要: ${testResults}"
                
                // 如果启用清理，则清理工作空间
                if (params.CLEAN_WORKSPACE) {
                    echo "清理工作空间..."
                    // 只清理临时文件，保留报告和日志
                    sh '''
                        rm -rf ${PYTHON_ENV}
                        rm -rf __pycache__
                        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
                        find . -type f -name "*.pyc" -delete 2>/dev/null || true
                    '''
                }
            }
        }

        success {
            script {
                echo "✅ 所有测试通过！"
                // 可以添加成功通知，如邮件、Slack 等
                // emailext(
                //     subject: "✅ 测试通过: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                //     body: "构建成功！\n\n查看详情: ${env.BUILD_URL}",
                //     to: "team@example.com"
                // )
            }
        }

        failure {
            script {
                echo "❌ 测试失败！"
                // 可以添加失败通知
                // emailext(
                //     subject: "❌ 测试失败: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                //     body: "构建失败！\n\n查看详情: ${env.BUILD_URL}\n\n查看日志: ${env.BUILD_URL}console",
                //     to: "team@example.com"
                // )
            }
        }

        unstable {
            script {
                echo "⚠️ 测试不稳定！"
            }
        }

        cleanup {
            script {
                echo "清理阶段..."
            }
        }
    }
}

// 构建测试命令的函数
def buildTestCommand() {
    def baseCommand = "pytest"
    def options = []
    
    // 添加详细输出
    options.add("-v")
    
    // 添加 Allure 结果目录
    options.add("--alluredir=${ALLURE_RESULTS_DIR}")
    options.add("--clean-alluredir")
    
    // 并行执行
    if (PARALLEL_WORKERS != '1') {
        options.add("-n ${PARALLEL_WORKERS}")
    }
    
    // 根据测试类型选择测试路径和标记
    switch(params.TEST_TYPE) {
        case 'ui':
            options.add("tests/ui")
            options.add("-m ui")
            break
        case 'api':
            options.add("tests/api")
            options.add("-m api")
            break
        case 'smoke':
            options.add("tests/")
            options.add("-m smoke")
            break
        case 'regression':
            options.add("tests/")
            options.add("-m regression")
            break
        default:
            options.add("tests/")
            break
    }
    
    // 添加自定义标记
    if (params.TEST_MARKERS?.trim()) {
        options.add("-m \"${params.TEST_MARKERS}\"")
    }
    
    // 添加超时设置（每个测试最多30分钟）
    options.add("--timeout=1800")
    
    // 添加失败重试（最多重试2次）
    options.add("--reruns=2")
    options.add("--reruns-delay=2")
    
    // 组合命令
    return "${baseCommand} ${options.join(' ')}"
}
