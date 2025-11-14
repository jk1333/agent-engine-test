# agent-engine-test

Google Cloud의 Agent Engine 실습에 사용되는 데모 프로젝트 입니다. Agent 예제는 ['Diatery_Planner'](https://medium.com/google-cloud/diatery-planner-your-ai-powered-recipe-diet-planner-with-googles-adk-5c402802c094)를 참고했습니다. Agent Starter Pack은 다음을 참고합니다. [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) version `0.16.0`

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


*1. 프로젝트에 로그인 한 뒤, 우측 상단의 속성 메뉴에 들어가서 Project settings 를 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/1.png)

*2. 메뉴에 들어가면 아래 그림과 같이 Project ID 값을 볼 수 있습니다. 이 값을 메모해 둡니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/2.png)

*3. 상단 검색 메뉴에서 'colab' 을 타이핑 하면 검색되는 'Colab Enterprise'를 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/3.png)

*4. 만약 아래와 같이 API Enable 이 필요하다고 하면 활성화를 합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/4.png)

*5. Import notebooks 를 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/5.png)

*6. 아래 그림과 같이 2개의 노트북 주소를 입력하고 Import 버튼을 누릅니다.

```code
https://github.com/jk1333/agent-engine-test/blob/main/notebooks/agentengine_evaluation.ipynb
```
```code
https://github.com/jk1333/agent-engine-test/blob/main/notebooks/agentengine_testing.ipynb
```
![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/6.png)

*7. 좌측의 메뉴에서 My notebooks 를 클릭한 뒤, agentengine_evaluation.ipynb 를 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/7.png)

*8. 우측의 연결을 클릭 후 런타임에 연결을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/8.png)

*9. Create new Runtime 을 선택한 후 Create Default Runtime을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/9.png)

*10. Open OAuth popup 이 나오면 Open 을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/10.png)

*11. student- 로 시작하는 계정을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/11.png)

*12. 우측 상단의 연결 중 상태가 지속된다면, 우측 상단에서 런타임에 연결을 클릭한 후 생성된 런타임에 Connect를 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/12.png)

*13. 아래 그림과 같이 연결이 완료되기까지 기다립니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/13.png)

*14. 연결이 완료되면 아래 그림과 같이 순차적으로 버튼을 클릭합니다. (수행이 완료될때 까지 약 3분정도 필요합니다.)

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/14.png)

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/14-1.png)

*15. 수행이 완료되면 메뉴에서 런타임을 클릭 후 세션 다시 시작을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/15.png)

*16. 하단의 터미널을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/16.png)

*17. 터미널이 나오면 아래의 명령어를 순차적으로 입력합니다. (배포가 완료될때 까지 10분 이상 필요합니다.)
```code
cd agent-engine-test
make backend
```
![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/17.png)

*18. 배포가 완료되면 아래 그림과 같이 화면이 표시됩니다. Agent Engine ID값을 아래 그림과 확이 확인 후 메모해 둡니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/18.png)

*19. 메모한 Project ID와 Agent Engine ID 값을 열려있는 노트북 파일의 3번째 셀의 PROJECT_ID, AGENT_ENGINE_ID 값에 업데이트 합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/19.png)

*20. 좌측의 메뉴에서 Agent Engine 을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/20.png)

*21. 배포된 Agent Engine 을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/21.png)

*22. Telemetry API 를 활성화 해야한다는 안내 메세지가 나온다면 Enable 을 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/22.png)

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/22-1.png)

*23. Playground 메뉴에 들어가서 다양한 대화를 해봅니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/23.png)

*24. 다양한 대화 후 Memories 메뉴에 들어가서 내가 발화한 내용이 메모리로 기억되었는지 확인합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/24.png)

*25. Dashboard, Traces, Sessions 메뉴를 클릭하며 기능들을 살펴보도록 합니다.

*26. Colab Enterprise 로 돌아와서 마지막 열었던 agentengine_evaluation.ipynb 를 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/26.png)

*27. 마지막 실행한 다음 셀 부터 실행 버튼을 클릭하며 수행 결과를 살펴봅니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/27.png)

*28. Evaluation 결과도 살펴봅니다.
![image](https://raw.githubusercontent.com/jk1333/handson/main/images/4/28.png)