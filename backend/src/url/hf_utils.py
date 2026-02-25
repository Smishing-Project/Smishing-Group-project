"""
Hugging Face Hub에서 모델 다운로드 및 로드
"""

import os
import joblib
from huggingface_hub import hf_hub_download


def download_model_from_hf(
    repo_id: str,
    local_dir: str = '/app/models',
    force_download: bool = False
):
    """
    Hugging Face Hub에서 모델 다운로드
    
    Args:
        repo_id: Hugging Face repository ID (예: "username/url-phishing-detector")
        local_dir: 로컬 저장 디렉토리
        force_download: 강제 재다운로드 여부
    
    Returns:
        dict: 다운로드된 파일 경로
    """
    print(f"📥 Hugging Face에서 모델 다운로드 중...")
    print(f"   Repository: {repo_id}")
    
    os.makedirs(local_dir, exist_ok=True)
    
    files_to_download = [
        'url_classifier.pkl',
        'feature_names.pkl',
        'metadata.pkl'
    ]
    
    downloaded_paths = {}
    
    for filename in files_to_download:
        try:
            # Hugging Face Hub에서 다운로드
            file_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=local_dir,
                force_download=force_download
            )
            
            # 파일을 models 디렉토리로 복사
            import shutil
            dest_path = os.path.join(local_dir, filename)
            shutil.copy(file_path, dest_path)
            
            downloaded_paths[filename] = dest_path
            print(f"   ✅ {filename}")
            
        except Exception as e:
            print(f"   ❌ {filename} 다운로드 실패: {e}")
            return None
    
    print(f"\n✅ 모델 다운로드 완료!")
    print(f"📁 저장 위치: {local_dir}")
    
    return downloaded_paths


def load_model_from_hf(repo_id: str):
    """
    Hugging Face Hub에서 모델을 다운로드하고 로드
    
    Args:
        repo_id: Hugging Face repository ID
    
    Returns:
        tuple: (model, feature_names, metadata)
    """
    try:
        # 모델 파일 다운로드
        model_path = hf_hub_download(repo_id=repo_id, filename="url_classifier.pkl")
        feature_path = hf_hub_download(repo_id=repo_id, filename="feature_names.pkl")
        metadata_path = hf_hub_download(repo_id=repo_id, filename="metadata.pkl")
        
        # 로드
        model = joblib.load(model_path)
        feature_names = joblib.load(feature_path)
        metadata = joblib.load(metadata_path)
        
        print(f"✅ Hugging Face에서 모델 로드 완료")
        print(f"   Repository: {repo_id}")
        print(f"   Accuracy: {metadata.get('accuracy', 0):.2%}")
        
        return model, feature_names, metadata
        
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return None, None, None


# 사용 예시
if __name__ == "__main__":
    # Hugging Face에서 모델 다운로드
    REPO_ID = "your-username/url-phishing-detector"  # 본인 것으로 변경
    
    # 방법 1: 다운로드만
    paths = download_model_from_hf(REPO_ID)
    
    if paths:
        print("\n다운로드된 파일:")
        for filename, path in paths.items():
            print(f"  - {filename}: {path}")
    
    # 방법 2: 다운로드 + 로드
    # model, features, metadata = load_model_from_hf(REPO_ID)
