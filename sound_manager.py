import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.bgm_volume = 0.6
        self.sfx_volume = 0.5
        self.current_bgm = None
        
        # 사운드 파일 자동 로드
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sounds_dir = os.path.join(script_dir, "sounds")
        
        # BGM 파일 로드 (sounds/bgm/ 폴더)
        self.bgm_files = {}
        bgm_dir = os.path.join(sounds_dir, "bgm")
        if os.path.exists(bgm_dir):
            for filename in os.listdir(bgm_dir):
                if filename.endswith(('.ogg', '.wav', '.mp3')):
                    filepath = os.path.join(bgm_dir, filename)
                    try:
                        sound = pygame.mixer.Sound(filepath)
                        # BGM은 긴 파일이므로 Sound 객체로 저장
                        self.bgm_files[filename] = sound
                    except:
                        pass
        
        # 효과음 파일 로드 (sounds/sfx/ 폴더)
        self.sfx_files = {}
        sfx_dir = os.path.join(sounds_dir, "sfx")
        if os.path.exists(sfx_dir):
            for filename in os.listdir(sfx_dir):
                if filename.endswith(('.ogg', '.wav', '.mp3')):
                    filepath = os.path.join(sfx_dir, filename)
                    try:
                        sound = pygame.mixer.Sound(filepath)
                        sound.set_volume(self.sfx_volume)
                        # 파일명에서 확장자 제거하여 키로 사용
                        key = os.path.splitext(filename)[0]
                        self.sfx_files[key] = sound
                    except:
                        pass
    
    def set_bgm_volume(self, volume):
        """BGM 볼륨 설정 (0.0 ~ 1.0)"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        if self.current_bgm:
            pygame.mixer.music.set_volume(self.bgm_volume)
    
    def set_sfx_volume(self, volume):
        """효과음 볼륨 설정 (0.0 ~ 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sfx_files.values():
            sound.set_volume(self.sfx_volume)
    
    def play_bgm(self, loop=-1):
        """BGM 재생 (loop=-1: 무한 반복, 0: 한 번만)"""
        # 첫 번째 BGM 파일 재생 (있는 경우)
        if self.bgm_files:
            bgm_name = list(self.bgm_files.keys())[0]
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bgm_path = os.path.join(script_dir, "sounds", "bgm", bgm_name)
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(loop)
                self.current_bgm = "playing"  # 재생 중임을 표시
            except:
                pass
    
    def pause_bgm(self):
        """BGM 일시정지"""
        if self.current_bgm:
            pygame.mixer.music.pause()
    
    def unpause_bgm(self):
        """BGM 재개"""
        if self.current_bgm:
            pygame.mixer.music.unpause()
    
    def stop_bgm(self):
        """BGM 정지"""
        pygame.mixer.music.stop()
        self.current_bgm = None
    
    def play_sfx(self, name):
        """효과음 재생 (파일명에서 확장자 제거한 이름 사용)"""
        if name in self.sfx_files:
            self.sfx_files[name].play()


def init_sound_manager():
    """SoundManager 인스턴스 생성 및 반환"""
    return SoundManager()
