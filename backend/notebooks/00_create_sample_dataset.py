"""
샘플 URL 데이터셋 생성 스크립트
테스트 및 프로토타입용 샘플 데이터 생성
"""

import pandas as pd
import os

# 데이터 저장 디렉토리
DATA_DIR = '/app/data/urls'
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

# 디렉토리 생성
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def create_sample_dataset():
    """샘플 데이터셋 생성"""
    
    # 악성 URL 샘플 (피싱, 스미싱 스타일)
    malicious_urls = [
        # 피싱 - 브랜드 사칭
        "http://paypal-secure-login.com/verify",
        "http://amazon-account-verify.com/update",
        "http://apple-id-locked.com/unlock",
        "http://netflix-payment-failed.com/update",
        "http://google-security-alert.com/verify",
        "http://microsoft-account-suspended.com/restore",
        "http://facebook-unusual-activity.com/verify",
        "http://instagram-verify-account.com/confirm",
        
        # 스미싱 - 택배/배송
        "http://cj-delivery-notice.com/parcel",
        "http://hanjin-package-arrived.com/check",
        "http://post-office-notice.com/delivery",
        "http://fedex-customs-clearance.com/pay",
        
        # IP 주소 사용
        "http://192.168.1.100/admin/login",
        "http://203.45.67.89/secure/verify",
        "http://10.0.0.1/banking/update",
        
        # 단축 URL (의심)
        "http://bit.ly/free-iphone-giveaway",
        "http://t.co/win-prize-now",
        
        # 의심스러운 패턴
        "http://secure-banking-update-urgent.com",
        "http://verify-your-account-now-2024.com",
        "http://claim-your-reward-immediately.com",
        "http://urgent-action-required-today.com",
        "http://limited-time-offer-act-now.com",
        "http://congratulations-winner-click-here.com",
        "http://account-locked-verify-identity.com",
        "http://suspicious-activity-confirm-now.com",
        
        # 하이픈 과다
        "http://pay-pal-secure-login-verify.com",
        "http://face-book-account-recovery.com",
        "http://goo-gle-security-check.com",
        
        # 숫자/특수문자 과다
        "http://paypa1-secure123.com",
        "http://amaz0n-verify456.com",
        "http://g00gle-alert789.com",
    ]
    
    # 정상 URL 샘플
    benign_urls = [
        # 글로벌 대형 사이트
        "https://www.google.com",
        "https://www.youtube.com",
        "https://www.facebook.com",
        "https://www.amazon.com",
        "https://www.wikipedia.org",
        "https://www.twitter.com",
        "https://www.instagram.com",
        "https://www.linkedin.com",
        "https://www.reddit.com",
        "https://www.netflix.com",
        
        # 한국 주요 사이트
        "https://www.naver.com",
        "https://www.daum.net",
        "https://www.kakao.com",
        "https://www.coupang.com",
        "https://www.11st.co.kr",
        "https://www.gmarket.co.kr",
        "https://www.auction.co.kr",
        "https://www.yes24.com",
        "https://www.aladin.co.kr",
        "https://www.interpark.com",
        
        # 기술/개발
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.medium.com",
        "https://www.dev.to",
        "https://www.hackerrank.com",
        
        # 뉴스/미디어
        "https://www.bbc.com",
        "https://www.cnn.com",
        "https://www.nytimes.com",
        "https://www.guardian.com",
        
        # 쇼핑/이커머스
        "https://www.ebay.com",
        "https://www.walmart.com",
        "https://www.target.com",
        "https://www.bestbuy.com",
    ]
    
    # 데이터프레임 생성
    df = pd.DataFrame({
        'url': malicious_urls + benign_urls,
        'label': [1] * len(malicious_urls) + [0] * len(benign_urls)
    })
    
    # 셔플
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # 저장
    output_path = os.path.join(RAW_DIR, 'sample_dataset.csv')
    df.to_csv(output_path, index=False)
    
    print(f"✅ 샘플 데이터셋 생성 완료!")
    print(f"📁 저장 위치: {output_path}")
    print(f"📊 데이터 통계:")
    print(f"   - 전체 URL: {len(df)}개")
    print(f"   - 악성 URL: {len(malicious_urls)}개 ({len(malicious_urls)/len(df)*100:.1f}%)")
    print(f"   - 정상 URL: {len(benign_urls)}개 ({len(benign_urls)/len(df)*100:.1f}%)")
    
    return df


if __name__ == "__main__":
    df = create_sample_dataset()
    
    # 샘플 출력
    print("\n📝 샘플 데이터 (처음 10개):")
    print(df.head(10))
