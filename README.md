<h2 align="center"> Requirements </h2>

- Chrome
- Python 3.11.7
- Install [pipx](https://pipx.pypa.io/stable/installation/)
- Install [Poetry 1.8.1](https://python-poetry.org/docs/#installation): `pipx install poetry==1.8.1`
- Install [CUDA 121](https://developer.nvidia.com/cuda-12-1-0-download-archive)


<h2 align="center"> What did we support </h2>

- Trade with Futu
- Train model with [FinRL](https://github.com/AI4Finance-Foundation/FinRL.git)



<h2 align="center"> Init project </h2>

- Go to the root of this project
- Execute `poetry shell`
- Execute `python install.py`
   
<h2 align="center"> Realtime data account setup </h2>

- The free user can get 5 requests per second and 500,000 requests per month, for Polygon API. Register [Here](https://polygon.io/docs)
- Setup the environment, on windows set the env directly, on mac execute `vim ~/.zshrc` append `export POLYGON_API_KEY=xxx` to the end of file, save the file execute `source ~/.zshrc`

<h2 align="center"> Paper trading account setup </h2>

- Each user can have 3 paper trading account, each account have 100,000 dollar, for Alpaca API. Register [Here](https://app.alpaca.markets/paper/dashboard/overview)
- Config `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` to your environment


<h2 align="center"> Setup your Futu env </h2>

- Note FutuD is for develop usage, it is different from Futu Client, but the account is same with Futu Client
- Download and install [FutuD](https://www.futunn.com/en/download/OpenAPI)
- Open FutuD setup the listen port to: 11111
- Execute `python install.py`


<h2 align="center"> Try it out </h2>

- Run `poetry run python .\test\utils_test.py` to test all the utils in the project
- Run `poetry run python .\test\finrl_client_test.py.py` to train model
- Run `poetry run python .\tests\futu_client_test.py.py` to test setup with Futu