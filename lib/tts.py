import json
import requests
from typing import List, Union, Optional

class TTS:
    def __init__(self, _api_addr: str) -> None:
        self.api_addr: str = _api_addr
        self.mode: str = ""
        self.payload: dict = {}



    def post(self) -> Optional[requests.Response]:
        url = f"{self.api_addr}{self.mode}"
        #发POST请求给GPT_SoVits
        try:
            response: requests.Response = requests.post(url, json=self.payload, stream=True)
            return response
        except Exception as e:
            print(f"Post到{url}:{e}")
            return None
        
        

class Infer(TTS):
    def __init__(self,
                _api_addr: str,
                _text: str,
                _text_lang: str,
                _ref_audio_path: str,
                _prompt_lang: str,
                _prompt_text: str = "",
                _aux_ref_audio_paths: Optional[List[str]] = None,
                _top_k: int = 15,
                _top_p: float = 1.0,
                _temperature: float = 1.0,
                _text_split_method: str = "cut5",
                _batch_size: int = 1,
                _batch_threshold: float = 0.75,
                _split_bucket: bool = True,
                _speed_factor: float = 1.0,
                _fragment_interval: float = 0.3,
                _seed: int = -1,
                _parallel_infer: bool = True,
                _repetition_penalty: float = 1.35,
                _sample_steps: int = 32,
                _super_sampling: bool = False,
                _streaming_mode: Union[bool, int] = False,
                _overlap_length: int = 2,
                _min_chunk_length: int = 16
                ) -> None:
        super().__init__(_api_addr)
        self.mode: str = "/tts"
        
        if _aux_ref_audio_paths is None:
            _aux_ref_audio_paths = []

        self.payload = {
            "text": _text,
            "text_lang": _text_lang,
            "ref_audio_path": _ref_audio_path,
            "aux_ref_audio_paths": _aux_ref_audio_paths,
            "prompt_text": _prompt_text,
            "prompt_lang": _prompt_lang,
            "top_k": _top_k,
            "top_p": _top_p,
            "temperature": _temperature,
            "text_split_method": _text_split_method,
            "batch_size": _batch_size,
            "batch_threshold": _batch_threshold,
            "split_bucket": _split_bucket,
            "speed_factor": _speed_factor,
            "fragment_interval": _fragment_interval,
            "seed": _seed,
            "parallel_infer": _parallel_infer,
            "repetition_penalty": _repetition_penalty,
            "sample_steps": _sample_steps,
            "super_sampling": _super_sampling,
            "streaming_mode": _streaming_mode,
            "overlap_length": _overlap_length,
            "min_chunk_length": _min_chunk_length,
        }
        
        
class Control(TTS):
    def __init__(self,
                _api_addr: str,
                _command: str
                ) -> None:
        super().__init__(_api_addr)
        self.mode: str = "/control"
        self.payload = {
            "command" : _command
        }
        
class GPT(TTS):
    def __init__(self, _api_addr: str, _weights_path: str) -> None:
        super().__init__(_api_addr)
        self.mode: str = "/set_gpt_weights"
        self.payload = {
            "weights_path": _weights_path
        }
        
class Sovits(TTS):
    def __init__(self, _api_addr: str, _weights_path: str) -> None:
        super().__init__(_api_addr)
        self.mode: str = "/set_sovits_weights"
        self.payload = {
            "weights_path": _weights_path
        }
        
        
    
        
    
    