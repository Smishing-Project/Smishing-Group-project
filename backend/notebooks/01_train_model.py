"""
URL 피싱 탐지 모델 학습 스크립트
Random Forest 모델 학습 및 평가
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import joblib
import os
import sys

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, '/app')

from src.url.feature_extractor import URLFeatureExtractor


# 경로 설정
DATA_DIR = '/app/data/urls'
MODEL_DIR = '/app/models'
os.makedirs(MODEL_DIR, exist_ok=True)


def load_dataset(filepath):
    """데이터셋 로드"""
    print(f"\n📂 데이터셋 로드: {filepath}")
    df = pd.read_csv(filepath)
    print(f"   - 전체: {len(df)}개")
    print(f"   - 악성: {(df['label']==1).sum()}개")
    print(f"   - 정상: {(df['label']==0).sum()}개")
    return df


def extract_features_from_dataset(df):
    """데이터셋의 모든 URL에서 특징 추출"""
    print("\n🔍 특징 추출 시작...")
    
    extractor = URLFeatureExtractor()
    features_list = []
    
    for idx, url in enumerate(df['url']):
        if idx % 10 == 0:
            print(f"   진행: {idx}/{len(df)} ({idx/len(df)*100:.1f}%)", end='\r')
        
        features = extractor.extract_features(url)
        features_list.append(features)
    
    print(f"   완료: {len(features_list)}/{len(df)} (100.0%)    ")
    
    # 특징을 DataFrame으로 변환
    features_df = pd.DataFrame(features_list)
    
    print(f"\n✅ 특징 추출 완료")
    print(f"   - 특징 개수: {len(features_df.columns)}개")
    
    return features_df


def train_model(X_train, y_train, X_test, y_test):
    """Random Forest 모델 학습"""
    print("\n🤖 모델 학습 시작...")
    
    # Random Forest 모델 생성
    model = RandomForestClassifier(
        n_estimators=100,        # 트리 개수
        max_depth=20,            # 최대 깊이
        min_samples_split=5,     # 분할 최소 샘플
        min_samples_leaf=2,      # 리프 최소 샘플
        random_state=42,
        n_jobs=-1,               # 병렬 처리
        verbose=1
    )
    
    # 학습
    model.fit(X_train, y_train)
    
    print("✅ 모델 학습 완료")
    
    # 평가
    print("\n📊 모델 평가...")
    
    # Train 성능
    train_pred = model.predict(X_train)
    train_acc = accuracy_score(y_train, train_pred)
    print(f"\n[Train 성능]")
    print(f"   - Accuracy: {train_acc:.4f}")
    
    # Test 성능
    test_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, test_pred)
    test_precision = precision_score(y_test, test_pred)
    test_recall = recall_score(y_test, test_pred)
    test_f1 = f1_score(y_test, test_pred)
    
    print(f"\n[Test 성능]")
    print(f"   - Accuracy:  {test_acc:.4f}")
    print(f"   - Precision: {test_precision:.4f}")
    print(f"   - Recall:    {test_recall:.4f}")
    print(f"   - F1-Score:  {test_f1:.4f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, test_pred)
    print(f"\n[Confusion Matrix]")
    print(f"   TN: {cm[0][0]}  FP: {cm[0][1]}")
    print(f"   FN: {cm[1][0]}  TP: {cm[1][1]}")
    
    # 상세 리포트
    print(f"\n[Classification Report]")
    print(classification_report(y_test, test_pred, 
                                target_names=['Benign', 'Malicious']))
    
    # 특징 중요도
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n[상위 10개 중요 특징]")
    for idx, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']:30s}: {row['importance']:.4f}")
    
    return model, feature_importance


def save_model(model, feature_names, metrics):
    """모델 및 메타데이터 저장"""
    print("\n💾 모델 저장 중...")
    
    # 모델 저장
    model_path = os.path.join(MODEL_DIR, 'url_classifier.pkl')
    joblib.dump(model, model_path)
    print(f"   ✅ 모델: {model_path}")
    
    # 특징 이름 저장
    feature_path = os.path.join(MODEL_DIR, 'feature_names.pkl')
    joblib.dump(feature_names, feature_path)
    print(f"   ✅ 특징: {feature_path}")
    
    # 메타데이터 저장
    metadata = {
        'model_type': 'RandomForest',
        'n_features': len(feature_names),
        'metrics': metrics,
        'trained_at': pd.Timestamp.now().isoformat()
    }
    
    metadata_path = os.path.join(MODEL_DIR, 'metadata.pkl')
    joblib.dump(metadata, metadata_path)
    print(f"   ✅ 메타데이터: {metadata_path}")
    
    print("\n✅ 모든 파일 저장 완료!")


def main():
    """전체 파이프라인 실행"""
    print("="*60)
    print("🚀 URL 피싱 탐지 모델 학습 시작")
    print("="*60)
    
    # 1. 데이터 로드
    dataset_path = os.path.join(DATA_DIR, 'raw', 'sample_dataset.csv')
    
    if not os.path.exists(dataset_path):
        print(f"❌ 데이터셋을 찾을 수 없습니다: {dataset_path}")
        print("   먼저 샘플 데이터셋을 생성하세요:")
        print("   python notebooks/00_create_sample_dataset.py")
        return
    
    df = load_dataset(dataset_path)
    
    # 2. 특징 추출
    features_df = extract_features_from_dataset(df)
    
    # 특징 저장 (선택)
    features_output = os.path.join(DATA_DIR, 'processed', 'features.csv')
    features_df.to_csv(features_output, index=False)
    print(f"   특징 저장: {features_output}")
    
    # 3. 데이터 분할
    print("\n📊 데이터 분할...")
    X = features_df
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"   - Train: {len(X_train)}개")
    print(f"   - Test:  {len(X_test)}개")
    
    # 4. 모델 학습
    model, feature_importance = train_model(X_train, y_train, X_test, y_test)
    
    # 5. 모델 저장
    test_pred = model.predict(X_test)
    metrics = {
        'accuracy': accuracy_score(y_test, test_pred),
        'precision': precision_score(y_test, test_pred),
        'recall': recall_score(y_test, test_pred),
        'f1_score': f1_score(y_test, test_pred)
    }
    
    save_model(model, list(X.columns), metrics)
    
    print("\n" + "="*60)
    print("🎉 모델 학습 완료!")
    print("="*60)
    
    # 목표 달성 여부
    print(f"\n🎯 목표 달성 여부:")
    print(f"   - Accuracy ≥ 85%: {'✅' if metrics['accuracy'] >= 0.85 else '❌'} ({metrics['accuracy']:.1%})")
    print(f"   - Recall ≥ 90%:   {'✅' if metrics['recall'] >= 0.90 else '❌'} ({metrics['recall']:.1%})")


if __name__ == "__main__":
    main()
