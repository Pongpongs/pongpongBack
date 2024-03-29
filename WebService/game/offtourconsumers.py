import json
import uuid
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asyncio import Lock
import time

class GameManager:
    def __init__(self):
        self.games = {}
        self.lock = Lock()
        self.room_sessions = {}

    def create_new_game_session(self, room_name):
        session_id = str(uuid.uuid4())
        self.room_sessions[room_name] = session_id
        self.games[session_id] = {
            'player1_id': 0,
            'player2_id': 0,
            'play_bar1_position': {'x': 0, 'y': 9},
            'play_bar2_position': {'x': 0, 'y': -9},
            'ball_position': {'x': 0, 'y': 0},
            'ball_velocity': {'x': 0.11, 'y': 0.08},
            'score_player1': 0,
            'score_player2': 0,
            'game_over_flag': False,
            'game_winner': 0,
            'updating_ball_position': False,
            'connected_clients_count': 0,
            'tournament_over_flag': False
        }
        return session_id

    async def increment_connected_clients(self, session_id):
        async with self.lock:
            self.games[session_id]['connected_clients_count'] += 1

    async def decrement_connected_clients(self, session_id):
        async with self.lock:
            self.games[session_id]['connected_clients_count'] -= 1
            if self.games[session_id]['connected_clients_count'] == 0:
                self.end_game_session(session_id)

    def get_game_state(self, session_id):
        return self.games.get(session_id)

    def end_game_session(self, session_id):
        if session_id in self.games:
            del self.games[session_id]


game_manager = GameManager()


class GameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.session_id = game_manager.create_new_game_session(self.room_name)
        self.game_state = game_manager.get_game_state(self.session_id)

        await self.channel_layer.group_add(self.session_id, self.channel_name)
        await self.accept()
        await game_manager.increment_connected_clients(self.session_id)

        self.heartbeat_interval = 10  # seconds
        self.last_heartbeat_time = time.time()
        self.heartbeat_task = asyncio.create_task(self.check_heartbeat())

        if self.game_state['connected_clients_count'] == 1:
            await asyncio.sleep(3)  # 클라이언트가 2개 연결된 후 3초 기다립니다.
            if not self.game_state['updating_ball_position']:
                self.game_state['updating_ball_position'] = True
                asyncio.create_task(self.ball_position_updater())

    async def disconnect(self, close_code):
        await game_manager.decrement_connected_clients(self.session_id)
        
        self.heartbeat_task.cancel()

        await self.channel_layer.group_discard(self.session_id, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # 이제 keyStates는 {"a": true/false, "d": true/false, "j": true/false, "l": true/false} 형태입니다.
        keyStates = text_data_json
        
        self.last_heartbeat_time = time.time()

        # 각 키에 대한 상태 확인 및 처리
        if keyStates.get('a'):
            self.game_state['play_bar1_position']['x'] = max(
                -9, self.game_state['play_bar1_position']['x'] - 0.4)
        if keyStates.get('d'):
            self.game_state['play_bar1_position']['x'] = min(
                9, self.game_state['play_bar1_position']['x'] + 0.4)
        if keyStates.get('j'):
            self.game_state['play_bar2_position']['x'] = max(
                -9, self.game_state['play_bar2_position']['x'] - 0.4)
        if keyStates.get('l'):
            self.game_state['play_bar2_position']['x'] = min(
                9, self.game_state['play_bar2_position']['x'] + 0.4)

    async def _update_ball_position(self):
        # 공 위치 업데이트
        self.game_state['ball_position']['x'] += self.game_state['ball_velocity']['x']
        self.game_state['ball_position']['y'] += self.game_state['ball_velocity']['y']

        # 바와 공의 충돌 검사
        bar_width = 2  # 예시 값, 실제 바의 가로 길이에 맞게 조정
        ball_radius = 0.5  # 예시 값, 실제 공의 반지름에 맞게 조정

        if self.game_state['play_bar1_position']['y'] - ball_radius < self.game_state['ball_position']['y'] < self.game_state['play_bar1_position']['y'] + ball_radius \
                and self.game_state['play_bar1_position']['x'] - bar_width / 2 < self.game_state['ball_position']['x'] < self.game_state['play_bar1_position']['x'] + bar_width / 2:
            self.game_state['ball_velocity']['y'] *= -1  # y 방향 반전

        if self.game_state['play_bar2_position']['y'] - ball_radius < self.game_state['ball_position']['y'] < self.game_state['play_bar2_position']['y'] + ball_radius \
                and self.game_state['play_bar2_position']['x'] - bar_width / 2 < self.game_state['ball_position']['x'] < self.game_state['play_bar2_position']['x'] + bar_width / 2:
            self.game_state['ball_velocity']['y'] *= -1  # y 방향 반전

        if self.game_state['ball_position']['y'] <= -10 or self.game_state['ball_position']['y'] >= 10:
            if self.game_state['ball_position']['y'] > 10:
                self.game_state['score_player2'] += 1
            elif self.game_state['ball_position']['y'] < -10:
                self.game_state['score_player1'] += 1
            self.game_state['ball_position'] = {'x': 0, 'y': 0}
            await asyncio.sleep(2)

        if self.game_state['ball_position']['x'] <= -10 or self.game_state['ball_position']['x'] >= 10:
            self.game_state['ball_velocity']['x'] *= -1  # x 방향 반전

        if self.game_state['score_player1'] >= self.game_state.get('game_over_score', 1) or self.game_state['score_player2'] >= self.game_state.get('game_over_score', 1):
            self.game_state['game_over_flag'] = True
            self.game_state['game_winner'] = 1 if self.game_state['score_player1'] >= self.game_state.get(
                'game_over_score', 1) else 2

        await self.channel_layer.group_send(
            self.session_id,  # 세션 ID를 기반으로 그룹명 지정
            {
                'type': 'game_update',
                # 'game_state': self.game_state
                'player1_id': self.game_state['player1_id'],
                'player2_id': self.game_state['player2_id'],
                'play_bar1_position': self.game_state['play_bar1_position'],
                'play_bar2_position': self.game_state['play_bar2_position'],
                'ball_position': self.game_state['ball_position'],
                'score_player1': self.game_state['score_player1'],
                'score_player2': self.game_state['score_player2'],
                'game_over_flag': self.game_state['game_over_flag'],
                'game_winner': self.game_state['game_winner'],
                'tournament_over_flag': self.game_state['tournament_over_flag']
            }
        )

    async def refresh_game_state(self):
        self.game_state['updating_ball_position'] = False
        self.game_state['game_over_flag'] = False
        self.game_state['game_winner'] = 0
        self.game_state['play_bar1_position'] = {'x': 0, 'y': 9}
        self.game_state['play_bar2_position'] = {'x': 0, 'y': -9}
        self.game_state['ball_position'] = {'x': 0, 'y': 0}
        self.game_state['ball_velocity'] = {'x': 0.11, 'y': 0.08}
        self.game_state['score_player1'] = 0
        self.game_state['score_player2'] = 0
        self.game_state['tournament_over_flag'] = False

        await asyncio.sleep(3)

    
    async def check_heartbeat(self):
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                if time.time() - self.last_heartbeat_time > self.heartbeat_interval:
                    # Heartbeat timeout exceeded, close the connection
                    print("Heartbeat timeout, closing connection")
                    await self.close()
                    break
        except asyncio.CancelledError:
            # Expected on disconnect
            pass


    async def ball_position_updater(self):

        winner1 = 0  # 첫번째 게임의 승자가 저장
        winner2 = 0  # 두번째 게임의 승자가 저장됨.

        self.game_state['player1_id'] = 1
        self.game_state['player2_id'] = 2
        while not self.game_state['game_over_flag']:
            await self._update_ball_position()
            await asyncio.sleep(0.02)  # 50번의 업데이트가 1초 동안 진행됨
        winner1 = self.game_state['game_winner']
        await self.refresh_game_state()
        # 첫번째 경기 승자 저장
        
        print("aaaa " , winner1  ," ", winner2)

        self.game_state['player1_id'] = 3
        self.game_state['player2_id'] = 4
        while not self.game_state['game_over_flag']:
            await self._update_ball_position()
            await asyncio.sleep(0.02)  # 50번의 업데이트가 1초 동안 진행됨
        if self.game_state['game_winner'] == 1:
            winner2 = self.game_state['player1_id']
        elif self.game_state['game_winner'] == 2:
            winner2 = self.game_state['player2_id']
        await self.refresh_game_state()
        # 두번째 경기 승자 저장
        print("bbbb " , winner1  ," ", winner2)


        self.game_state['player1_id'] = winner1
        self.game_state['player2_id'] = winner2
        while not self.game_state['game_over_flag']:
            await self._update_ball_position()
            await asyncio.sleep(0.02)  # 50번의 업데이트가 1초 동안 진행됨
        
        await self.refresh_game_state()

        self.game_state['updating_ball_position'] = False
        self.game_state['game_over_flag'] = False
        self.game_state['game_winner'] = 0
        self.game_state['play_bar1_position'] = {'x': 0, 'y': 9}
        self.game_state['play_bar2_position'] = {'x': 0, 'y': -9}
        self.game_state['ball_position'] = {'x': 0, 'y': 0}
        self.game_state['ball_velocity'] = {'x': 0.11, 'y': 0.08}
        self.game_state['score_player1'] = 0
        self.game_state['score_player2'] = 0
        self.game_state['tournament_over_flag'] = True
        print("!!!!!!!!!!!!")

        await self.channel_layer.group_send(
            self.session_id,  # 세션 ID를 기반으로 그룹명 지정
            {
                'type': 'game_update',
                # 'game_state': self.game_state
                'player1_id': self.game_state['player1_id'],
                'player2_id': self.game_state['player2_id'],
                'play_bar1_position': self.game_state['play_bar1_position'],
                'play_bar2_position': self.game_state['play_bar2_position'],
                'ball_position': self.game_state['ball_position'],
                'score_player1': self.game_state['score_player1'],
                'score_player2': self.game_state['score_player2'],
                'game_over_flag': self.game_state['game_over_flag'],
                'game_winner': self.game_state['game_winner'],
                'tournament_over_flag': self.game_state['tournament_over_flag']
            }
        )

        # self._update_ball_position()
        game_manager.end_game_session(self.session_id)

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'player1_id': event['player1_id'],
            'player2_id': event['player2_id'],
            'play_bar1_position': event['play_bar1_position'],
            'play_bar2_position': event['play_bar2_position'],
            'ball_position': event['ball_position'],
            'score_player1': event['score_player1'],
            'score_player2': event['score_player2'],
            'game_over_flag': event['game_over_flag'],
            'game_winner': event['game_winner'],
            'tournament_over_flag': event['tournament_over_flag']
        }))
