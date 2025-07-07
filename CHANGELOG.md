# Changelog

## 0.1.0 (2025-07-07)


### Features

* add Dockerfile for containerized deployment ([98be58f](https://github.com/KKamJi98/kubernetes-dashboard/commit/98be58fdfc4f52460ad2e854e4da614700bf0c13))
* add kubeconfig management from Kubernetes secrets ([78675fb](https://github.com/KKamJi98/kubernetes-dashboard/commit/78675fbd276a1541e2c3c7a7f732b615015460bb))
* add Kubernetes deployment manifest with secret support ([91deb3d](https://github.com/KKamJi98/kubernetes-dashboard/commit/91deb3d476856680af5362c712e1f55d39fc3528))
* add logs/events page and auto-refresh functionality ([9ced877](https://github.com/KKamJi98/kubernetes-dashboard/commit/9ced87728f6f29a3c5be5bc6f35c4186d153658f))
* add percentage display for node resource usage ([0a129b3](https://github.com/KKamJi98/kubernetes-dashboard/commit/0a129b36caee69729e931ecd73f933078d01ac51))
* add pod logs and cluster events collection functions ([3572f0c](https://github.com/KKamJi98/kubernetes-dashboard/commit/3572f0c0ea5da31075863a4b960d687d612fcc01))
* add run_and_test.sh script for headless testing ([a306d97](https://github.com/KKamJi98/kubernetes-dashboard/commit/a306d97bcdbaa939307feb18b289fff7b61b9888))
* **cli:** 실행 스크립트 및 진입점 추가 ([70525a2](https://github.com/KKamJi98/kubernetes-dashboard/commit/70525a2ea21893c971542a5dab46383888bd6a5a))
* **collectors:** 멀티 클러스터 데이터 수집 모듈 구현 ([af56631](https://github.com/KKamJi98/kubernetes-dashboard/commit/af56631aec9e28f05b5698726ea7fe26258732d8))
* migrate from poetry to uv package manager ([a8248c4](https://github.com/KKamJi98/kubernetes-dashboard/commit/a8248c4cecf366a46c00f32b440e0597db5ec923))
* **test:** 테스트용 Kubernetes 매니페스트 파일 추가 ([c884e8f](https://github.com/KKamJi98/kubernetes-dashboard/commit/c884e8fb0a487355c09005639d263ee3ff36df1a))
* **ui:** Streamlit 기반 대시보드 UI 구현 ([d2da710](https://github.com/KKamJi98/kubernetes-dashboard/commit/d2da71023d12830de5e90e0c5e84edba813f65fc))
* 노드 리소스 사용량 퍼센트 표시 기능 추가 ([e77d891](https://github.com/KKamJi98/kubernetes-dashboard/commit/e77d8912d684b618680a55ef9d765b663d1fa8bb))


### Bug Fixes

* metrics-server 없는 경우 에러 처리 및 문서 업데이트 ([125955c](https://github.com/KKamJi98/kubernetes-dashboard/commit/125955cc058a20925ed2d3b832e3da15191d8b2e))
* resolve test failures and format code ([c71a448](https://github.com/KKamJi98/kubernetes-dashboard/commit/c71a4488eff1c2d8f14a05c1c1f33b3e1b817aa0))
* update test_kube_client.py to handle cache_clear ([0407568](https://github.com/KKamJi98/kubernetes-dashboard/commit/0407568af0ff0650ab7c3a60b82312a2cff9bf5a))


### Documentation

* Add black and isort integration details to project requirements ([e9f5f26](https://github.com/KKamJi98/kubernetes-dashboard/commit/e9f5f264f51362f91cdcba357623c28204cf6b54))
* Add code quality management section to project requirements ([1d81b07](https://github.com/KKamJi98/kubernetes-dashboard/commit/1d81b070b0385e1d9d88b6ee795690a8ca23aa52))
* update README with new features and installation instructions ([acbc384](https://github.com/KKamJi98/kubernetes-dashboard/commit/acbc3842bbb32c20cbbcf2878f5989f89d2de5ef))
* update README.md with latest features and usage instructions ([bd4f834](https://github.com/KKamJi98/kubernetes-dashboard/commit/bd4f834577d40ec1c7fc1daf1667944e8dbd3991))
* Update README.md with project information ([41bfb0d](https://github.com/KKamJi98/kubernetes-dashboard/commit/41bfb0d9eaab91f10e5067718ce3f35d15698206))
* 프로젝트 문서 및 설정 파일 추가 ([90ed4ab](https://github.com/KKamJi98/kubernetes-dashboard/commit/90ed4ab4653847235c7285151ba0472453403318))
