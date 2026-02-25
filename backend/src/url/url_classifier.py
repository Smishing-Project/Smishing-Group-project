"""
URL 분류기 모듈
학습된 Random Forest 모델로 URL 위험도 예측
"""

import joblib
import os
from typing import Dict
import numpy as np

from src.url.feature_extractor import URLFeatureExtractor


class URLClassifier:
    """학습된 ML 모델로 URL 분류"""
    
    def __init__(self, model_dir: str = '/app/models'):
        """
        URL 분류기 초기화
        
        Args:
            model_dir: 모델 파일이 저장된 디렉토리
        """
        self.model_dir = model_dir
        self.model = None
        self.feature_names = None
        self.metadata = None
        self.feature_extractor = URLFeatureExtractor()
        
        # 모델 로드 시도
        self._load_model()
    
    def _load_model(self):
        """저장된 모델 로드"""
        model_path = os.path.join(self.model_dir, 'url_classifier.pkl')
        feature_path = os.path.join(self.model_dir, 'feature_names.pkl')
        metadata_path = os.path.join(self.model_dir, 'metadata.pkl')
        
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.feature_names = joblib.load(feature_path)
                self.metadata = joblib.load(metadata_path)
                
                print(f"✅ URL Classifier 모델 로드 완료")
                print(f"   - 모델: {self.metadata.get('model_type', 'Unknown')}")
                print(f"   - Accuracy: {self.metadata.get('accuracy', 0):.2%}")
                print(f"   - Recall: {self.metadata.get('recall', 0):.2%}")
            except Exception as e:
                print(f"⚠️ 모델 로드 실패: {e}")
                self.model = None
        else:
            print(f"ℹ️ 학습된 모델이 없습니다: {model_path}")
            print(f"   Google Colab에서 모델을 학습 후 업로드하세요.")
            self.model = None
    
    def is_model_loaded(self) -> bool:
        """모델이 로드되었는지 확인"""
        return self.model is not None
    
    def predict(self, url: str) -> Dict[str, any]:
        """
        URL의 악성 여부 예측
        
        Args:
            url: 예측할 URL
        
        Returns:
            dict: {
                'is_malicious': bool,
                'confidence': float,
                'probability': dict,
                'features': dict
            }
        """
        if not self.is_model_loaded():
            return {
                'is_malicious': False,
                'confidence': 0.0,
                'probability': {'benign': 0.5, 'malicious': 0.5},
                'features': {},
                'error': 'Model not loaded'
            }
        
        try:
            # 특징 추출
            features = self.feature_extractor.extract_features(url)
            
            # 특징을 DataFrame으로 변환 (모델 학습 시 순서와 동일하게)
            import pandas as pd
            features_df = pd.DataFrame([features])[self.feature_names]
            
            # 예측
            prediction = self.model.predict(features_df)[0]
            probabilities = self.model.predict_proba(features_df)[0]
            
            return {
                'is_malicious': bool(prediction == 1),
                'confidence': float(probabilities[prediction]),
                'probability': {
                    'benign': float(probabilities[0]),
                    'malicious': float(probabilities[1])
                },
                'features': features
            }
            
        except Exception as e:
            return {
                'is_malicious': False,
                'confidence': 0.0,
                'probability': {'benign': 0.5, 'malicious': 0.5},
                'features': {},
                'error': f'Prediction failed: {str(e)}'
            }
    
    def predict_batch(self, urls: list) -> list:
        """
        여러 URL 일괄 예측
        
        Args:
            urls: URL 리스트
        
        Returns:
            list: 예측 결과 리스트
        """
        return [self.predict(url) for url in urls]


# 사용 예시
if __name__ == "__main__":
    classifier = URLClassifier()
    
    if classifier.is_model_loaded():
        # 테스트 URL
        test_urls = [
            "https://www.google.com",
            "http://paypal-secure-login.com/verify",
            "http://192.168.1.1/admin"
        ]
        
        for url in test_urls:
            print(f"\n🔍 URL: {url}")
            result = classifier.predict(url)
            
            if 'error' not in result:
                status = "악성" if result['is_malicious'] else "정상"
                print(f"   예측: {status} (신뢰도: {result['confidence']:.1%})")
                print(f"   확률: 정상 {result['probability']['benign']:.2%} | "
                      f"악성 {result['probability']['malicious']:.2%}")
            else:
                print(f"   오류: {result['error']}")
    else:
        print("\n⚠️ 모델이 로드되지 않았습니다.")
        print("   Google Colab에서 모델 학습 후 다음 파일을 업로드하세요:")
        print("   1. models/url_classifier.pkl")
        print("   2. models/feature_names.pkl")
        print("   3. models/metadata.pkl")
