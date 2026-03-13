# agent-engine-test

Google Cloud의 Agent Engine 실습에 사용되는 데모 프로젝트 입니다. 

Agent 예제는 ['Diatery_Planner'](https://medium.com/google-cloud/diatery-planner-your-ai-powered-recipe-diet-planner-with-googles-adk-5c402802c094)를 참고했습니다. 

Agent Starter Pack은 다음을 참고합니다. [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) version `0.16.0`

DB Session 을 이용시 Private network 에서의 DB 배포는 아래 메뉴얼을 따릅니다.

https://cloud.google.com/sql/docs/postgres/configure-private-service-connect?hl=ko

## Project Structure

폴더 구조는 아래를 따릅니다.:

```
agent-engine-test/
├── app/                 # Main application code
│   ├── agent.py         # Main agent (Root agent)
│   ├── sub_agents/      # Sub agent
│   ├── agent_engine_app.py # Agent Engine start code
│   └── utils/           # Utility functions and helpers
├── .cloudbuild/         # CI/CD pipeline configurations for Google Cloud Build
├── deployment/          # Infrastructure and deployment scripts
├── notebooks/           # Jupyter notebooks for prototyping and evaluation
├── tests/               # Unit, integration, and load tests
├── Makefile             # Makefile for common commands
├── GEMINI.md            # AI-assisted development guide
└── pyproject.toml       # Project dependencies and configuration
```

## Quick Start - Local 테스트

로컬 환경에서는 아래의 명령으로 테스트 환경(adk web)을 실행할 수 있습니다.

```bash
make install && make playground
```

## Quick Start - Agent Engine 으로 테스트 배포(DEV)

현재 프로젝트를 테스트 목적으로 Agent Engine 에 배포하고자 한다면 아래의 명령어를 실행 합니다.

```bash
make backend
```

## Quick Start - Agent Engine 으로 CI/CD 환경 구축(STG/PRD)

현재 프로젝트를 Agent Engine 으로 CI/CD 시스템을 구축하고자 한다면 아래의 명령어를 실행 합니다.

STG와 PRD 환경은 서로 다른 프로젝트를 이용해야 합니다.

```bash
agent-starter-pack setup-cicd --cicd-project [CI/CD 를 수행할 프로젝트ID] --staging-project [STG 환경 프로젝트ID] --prod-project [PRD 환경 프로젝트ID] --repository-name [리포지토리명]
```

## Commands

| 명령어                | 설명                                                                            |
| -------------------- | --------------------------------------------------------------------------------|
| `make install`       | uv 를 이용해 필요한 패키지를 설치합니다.                                           |
| `make playground`    | Agent 를 로컬에서 테스트할 수 있는 UI를 실행합니다. 좌측 상단에서 App을 선택합니다.  |
| `make backend`       | 현재의 구성을 Agent Engine 으로 배포합니다.                                        |
| `make test`          | 유닛 테스트와 통합 테스트를 수행합니다.                                            |
| `make lint`          | 코드 품질 체크를 실행합니다. (codespell, ruff, mypy)                              |
| `git push`           | CI/CD 파이프라인을 수행합니다.                                                    |


## Qwiklab 실습

아래의 내용은 Qwiklab 환경에서 본 프로젝트를 배포하고 실행하는 과정을 설명합니다.

#### 1. 상단 검색 메뉴에서 'workbench' 를 타이핑 하면 검색되는 'Workbench'를 클릭합니다.
![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/1.png)
***
<br>

#### 2. Workbench 터미널을 진입 후 아래의 명령어로 실습자료를 다운받습니다.

```
git clone https://github.com/jk1333/agent-engine-test
```

#### 3. 실습 자료가 다운되면 아래의 명령어로 예제 에이전트를 Agent Engine 으로 배포합니다.

```
pip install uv
cd agent-engine-test
make backend
```

#### 4. 배포가 완료되면 아래 그림과 같이 화면이 표시됩니다. Agent Engine ID값을 아래 그림과 같이 확인 후 메모해 둡니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/2.png)
***
<br>

#### 5. Jupyter lab 환경에서 좌측 메뉴에서 /agent-engine-test/notebooks/agentengine_evaluation.ipynb 를 클릭합니다.

#### 6. 네번째 셀에 AGENT_ENGINE_ID "00000000000" 으로 되어있는 부분을 메모한 Agent Engine ID 로 변경합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/4.png)
***
<br>

#### 7. Google Cloud 콘솔의 좌측 메뉴에서 Agent Engine 을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/3.png)
***
<br>

#### 8. 배포된 Agent Engine 을 확인 후 Recource name 은 별도 복사해 두고 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/5.png)
***
<br>

#### 9. Playground 메뉴에 들어가서 다양한 대화를 해봅니다.

Session 1 예시: 소고기 메뉴를 추천해 주세요.

Session 2 예시: 저 채식주의자 입니다.

Session 3 예시: 다시 소고기 메뉴를 추천해 주세요. 

(기대결과: 지난번 채식주의자라고 말씀 주셨기 때문에 그에 맞는 메뉴로 추천드립니다.)

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/6.png)
***
<br>

#### 10. 다양한 대화 후 Memories 메뉴에 들어가서 내가 발화한 내용이 메모리로 기억되었는지 확인합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/7.png)
***
<br>

#### 11. Dashboard, Traces, Sessions 메뉴를 클릭하며 기능들을 살펴보도록 합니다.

#### 12. Workbench 로 돌아와서 agentengine_evaluation.ipynb 를 수행합니다.

(현재 이슈로 동작 안함)

#### 13. Google Cloud 콘솔 검색 메뉴에서 "credentials" 혹은 "oauth" 를 검색하면 나오는 Credentials 를 클릭합니다.
![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/8.png)
***
<br>

Create credentials -> OAuth client ID 를 클릭합니다.

Application type: Web application

Name: Sample

Authorized redirect URI 는 다음을 입력 후 Create합니다.
```
https://vertexaisearch.cloud.google.com/oauth-redirect
```

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/9.png)
***
<br>

CLIENT_ID, CLIENT_SECRET 정보를 기록합니다.

#### 14. 13에서 획득한 정보 및 Agent Engine 의 Resource Name을 Makefile 에 업데이트 합니다.

Jupyter Lab 에서 /agent-engine-test/Makefile 을 열고 아래의 정보를 확인 후 기록해둔 값으로 업데이트 합니다.

```
CLIENT_ID := CLIENT_ID
CLIENT_SECRET := SECRET
AGENT_ENGINE_RESOURCE_NAME := FULL_RESOURCE_NAME
```

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/10.png)
***
<br>

#### 15. Google Cloud 콘솔에서 Gemini Enterprise 를 검색 후 메뉴로 진입합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/11.png)
***
<br>

#### 16. Gemini Enterprise 메뉴의 Settings 로 진입하여 Authentication settings 부분에 global 설정메뉴 진입 후 Google Identity 를 설정합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/12.png)
***
<br>

#### 17. Apps를 클릭 후 기 생성돼 있는 agent-portal 을 클릭합니다. Connected data stores 를 클릭, New data store 를 클릭 후 Google Drive 를 Select 합니다. Default 값 및 임의의 name 을 지정 후 생성합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/13.png)
***

#### 18. Jupyter Lab 의 Terminal 로 돌아와 아래의 명령어를 실행하여 에이전트를 Gemini Enterprise에 등록합니다.

```
make ge-register
```

#### 19. Gemini Enterprise 를 실행합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/14.png)
***
<br>

#### 20. GE 메뉴에서 에이전트를 클릭, 에이전트와 대화합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/15.png)
***
<br>

Authorize 버튼을 클릭합니다. 사용자의 Google Drive에 접근 권한을 부여합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/16.png)
***
<br>

"드라이브에 저장해줘" 와 같은 명령어를 통해 생성된 레시피를 저장하게 지시합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/17.png)
***
<br>

#### 21. drive.google.com 에 들어가서 파일이 생성됐는지 확인합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/6/18.png)
***
<br>

