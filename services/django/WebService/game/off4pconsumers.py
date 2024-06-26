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
            'play_bar1_position': {'x': 0, 'y': 9},
            'play_bar2_position': {'x': 0, 'y': -9},
            'play_bar3_position': {'x': 9, 'y': 0},
            'play_bar4_position': {'x': -9, 'y': 0},
            'ball_position': {'x': 0, 'y': 0},
            'ball_velocity': {'x': 0.06, 'y': 0.05},
            'score_player1': 0,
            'score_player2': 0,
            'score_player3': 0,
            'score_player4': 0,
            'game_over_flag': False,
            'game_winner': 0,
            'updating_ball_position': False,
            'connected_clients_count': 0
        }
        return session_id

    async def increment_connected_clients(self, session_id):
        async with self.lock:
            self.games[session_id]['connected_clients_count'] += 1

    async def decrement_connected_clients(self, session_id):
        async with self.lock:
            if session_id in self.games:
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



        if self.game_state['connected_clients_count'] == 1:
            await asyncio.sleep(3)  # 클라이언트가 2개 연결된 후 3초 기다립니다.
            if not self.game_state['updating_ball_position']:
                self.game_state['updating_ball_position'] = True
                asyncio.create_task(self.ball_position_updater())

    async def disconnect(self, close_code):
        await game_manager.decrement_connected_clients(self.session_id)

        await self.channel_layer.group_discard(self.session_id, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        keyStates = text_data_json


        if keyStates.get('q'):
            self.game_state['play_bar1_position']['x'] = max(
                -8, self.game_state['play_bar1_position']['x'] - 0.4)
        if keyStates.get('e'):
            self.game_state['play_bar1_position']['x'] = min(
                9, self.game_state['play_bar1_position']['x'] + 0.4)

        if keyStates.get('i'):
            self.game_state['play_bar2_position']['x'] = max(
                -9, self.game_state['play_bar2_position']['x'] - 0.4)
        if keyStates.get('p'):
            self.game_state['play_bar2_position']['x'] = min(
                8, self.game_state['play_bar2_position']['x'] + 0.4)

        if keyStates.get('z'):
            self.game_state['play_bar4_position']['y'] = max(
                -8, self.game_state['play_bar4_position']['y'] - 0.4)
        if keyStates.get('c'):
            self.game_state['play_bar4_position']['y'] = min(
                9, self.game_state['play_bar4_position']['y'] + 0.4)

        if keyStates.get('b'):
            self.game_state['play_bar3_position']['y'] = max(
                -9, self.game_state['play_bar3_position']['y'] - 0.4)
        if keyStates.get('m'):
            self.game_state['play_bar3_position']['y'] = min(
                8, self.game_state['play_bar3_position']['y'] + 0.4)

    async def _update_ball_position(self):
        # 공 위치 업데이트
        self.game_state['ball_position']['x'] += self.game_state['ball_velocity']['x']
        self.game_state['ball_position']['y'] += self.game_state['ball_velocity']['y']

        # 바와 공의 충돌 검사
        bar_width = 2  # 예시 값, 실제 바의 가로 길이에 맞게 조정
        ball_radius = 0.5  # 예시 값, 실제 공의 반지름에 맞게 조정

        # 첫 번째 플레이어 바와 공의 충돌 검사
        if self.game_state['play_bar1_position']['y'] - ball_radius < self.game_state['ball_position']['y'] < self.game_state['play_bar1_position']['y'] + ball_radius \
                and self.game_state['play_bar1_position']['x'] - bar_width / 2 < self.game_state['ball_position']['x'] < self.game_state['play_bar1_position']['x'] + bar_width / 2:
            self.game_state['ball_velocity']['y'] *= -1  # y 방향 반전

        # 두 번째 플레이어 바와 공의 충돌 검사
        if self.game_state['play_bar2_position']['y'] - ball_radius < self.game_state['ball_position']['y'] < self.game_state['play_bar2_position']['y'] + ball_radius \
                and self.game_state['play_bar2_position']['x'] - bar_width / 2 < self.game_state['ball_position']['x'] < self.game_state['play_bar2_position']['x'] + bar_width / 2:
            self.game_state['ball_velocity']['y'] *= -1  # y 방향 반전

        if self.game_state['play_bar3_position']['x'] - ball_radius < self.game_state['ball_position']['x'] < self.game_state['play_bar3_position']['x'] + ball_radius \
                and self.game_state['play_bar3_position']['y'] - bar_width / 2 < self.game_state['ball_position']['y'] < self.game_state['play_bar3_position']['y'] + bar_width / 2:
            self.game_state['ball_velocity']['x'] *= -1  # y 방향 반전

        if self.game_state['play_bar4_position']['x'] - ball_radius < self.game_state['ball_position']['x'] < self.game_state['play_bar4_position']['x'] + ball_radius \
                and self.game_state['play_bar4_position']['y'] - bar_width / 2 < self.game_state['ball_position']['y'] < self.game_state['play_bar4_position']['y'] + bar_width / 2:
            self.game_state['ball_velocity']['x'] *= -1  # y 방향 반전

        # 벽과의 충돌 처리
        if self.game_state['ball_position']['y'] <= -10 or self.game_state['ball_position']['y'] >= 10:
            if self.game_state['ball_position']['y'] > 10:
                self.game_state['score_player2'] += 1
            elif self.game_state['ball_position']['y'] < -10:
                self.game_state['score_player1'] += 1
            self.game_state['ball_position'] = {'x': 0, 'y': 0}
            self.game_state['play_bar1_position'] = {'x': 0, 'y': 9}
            self.game_state['play_bar2_position'] = {'x': 0, 'y': -9}
            self.game_state['play_bar3_position'] = {'x': 9, 'y': 0}
            self.game_state['play_bar4_position'] = {'x': -9, 'y': 0}
            await asyncio.sleep(2)

        if self.game_state['ball_position']['x'] <= -10 or self.game_state['ball_position']['x'] >= 10:
            if self.game_state['ball_position']['x'] > 10:
                self.game_state['score_player3'] += 1
            elif self.game_state['ball_position']['x'] < -10:
                self.game_state['score_player4'] += 1
            self.game_state['ball_position'] = {'x': 0, 'y': 0}
            self.game_state['play_bar1_position'] = {'x': 0, 'y': 9}
            self.game_state['play_bar2_position'] = {'x': 0, 'y': -9}
            self.game_state['play_bar3_position'] = {'x': 9, 'y': 0}
            self.game_state['play_bar4_position'] = {'x': -9, 'y': 0}
            await asyncio.sleep(2)

        #########################
        # 게임 종료 조건 확인
        if self.game_state['score_player1'] == 3:
            self.game_state['game_over_flag'] = True
            self.game_state['game_winner'] = 1

        if self.game_state['score_player2'] == 3:
            self.game_state['game_over_flag'] = True
            self.game_state['game_winner'] = 2

        if self.game_state['score_player3'] == 3:
            self.game_state['game_over_flag'] = True
            self.game_state['game_winner'] = 3

        if self.game_state['score_player4'] == 3:
            self.game_state['game_over_flag'] = True
            self.game_state['game_winner'] = 4

        await self.channel_layer.group_send(
            self.session_id,  # 세션 ID를 기반으로 그룹명 지정
            {
                'type': 'game_update',
                # 'game_state': self.game_state
                'play_bar1_position': self.game_state['play_bar1_position'],
                'play_bar2_position': self.game_state['play_bar2_position'],
                'play_bar3_position': self.game_state['play_bar3_position'],
                'play_bar4_position': self.game_state['play_bar4_position'],
                'ball_position': self.game_state['ball_position'],
                'score_player1': self.game_state['score_player1'],
                'score_player2': self.game_state['score_player2'],
                'score_player3': self.game_state['score_player3'],
                'score_player4': self.game_state['score_player4'],
                'game_over_flag': self.game_state['game_over_flag'],
                'game_winner': self.game_state['game_winner']
            }
        )

    async def ball_position_updater(self):

        while not self.game_state['game_over_flag']:
            await self._update_ball_position()
            await asyncio.sleep(0.02)  # 50번의 업데이트가 1초 동안 진행됨

        self.game_state['updating_ball_position'] = False
        self.game_state['game_over_flag'] = False
        self.game_state['game_winner'] = 0
        self.game_state['play_bar1_position'] = {'x': 0, 'y': 9}
        self.game_state['play_bar2_position'] = {'x': 0, 'y': -9}
        self.game_state['play_bar3_position'] = {'x': -9, 'y': 0}
        self.game_state['play_bar4_position'] = {'x': 9, 'y': 0}
        self.game_state['ball_position'] = {'x': 0, 'y': 0}
        self.game_state['ball_velocity'] = {'x': 0.06, 'y': 0.05}
        self.game_state['score_player1'] = 0
        self.game_state['score_player2'] = 0
        self.game_state['score_player3'] = 0
        self.game_state['score_player4'] = 0

        game_manager.end_game_session(self.session_id)



    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'play_bar1_position': event['play_bar1_position'],
            'play_bar2_position': event['play_bar2_position'],
            'play_bar3_position': event['play_bar3_position'],
            'play_bar4_position': event['play_bar4_position'],
            'ball_position': event['ball_position'],
            'score_player1': event['score_player1'],
            'score_player2': event['score_player2'],
            'score_player3': event['score_player3'],
            'score_player4': event['score_player4'],
            'game_over_flag': event['game_over_flag'],
            'game_winner': event['game_winner']
        }))
