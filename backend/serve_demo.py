"""Offline local launcher: deterministic data, optional archived reset, production UI."""
import argparse
from pathlib import Path
from dotenv import load_dotenv
from .prepare_demo import prepare,DEFAULT_STATE

if __name__=='__main__':
    # Local secrets stay outside source control and never enter the browser bundle.
    load_dotenv(Path(__file__).resolve().parents[1]/'.env',override=False)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir',default=str(DEFAULT_STATE));parser.add_argument('--reset',action='store_true');parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args();print(prepare(args.state_dir,args.reset),flush=True)
    import uvicorn
    uvicorn.run('backend.main:app',host='127.0.0.1',port=args.port)
