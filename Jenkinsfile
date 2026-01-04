pipeline {
    agent any

    environment {
        // 定义环境变量
        PYTHON_ENV = "${WORKSPACE}/venv"
    }

    stages {
        stage('Checkout') {
            steps {
                // 从Git拉取代码
                git branch: 'main',
                    url: 'https://github.com/cmrhyq/AUTestAutomation.git',
                    credentialsId: 'alan-github-ssh'
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    # 创建虚拟环境
                    python3 -m venv ${PYTHON_ENV}

                    # 激活虚拟环境并安装依赖
                    . ${PYTHON_ENV}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    # 激活虚拟环境
                    . ${PYTHON_ENV}/bin/activate

                    # 运行测试
                    # UI测试（headless模式）
                    pytest tests/ui_tests --html=reports/ui_report.html

                    # API测试
                    pytest tests/api_tests --html=reports/api_report.html

                    # 或者运行所有测试
                    # pytest tests/ --html=reports/test_report.html
                '''
            }
        }

        stage('Generate Allure Report') {
            steps {
                sh '''
                    . ${PYTHON_ENV}/bin/activate
                    pytest tests/ --alluredir=allure-results
                '''

                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }

    post {
        always {
            // 发布HTML报告
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: '*.html',
                reportName: 'Test Report',
                reportTitles: ''
            ])

            // 清理工作空间
            cleanWs()
        }

        success {
            echo 'Tests passed!'
            // 可以添加邮件通知等
        }

        failure {
            echo 'Tests failed!'
            // 发送失败通知
        }
    }
}
