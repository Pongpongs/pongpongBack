import json
import uuid
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
# //remote multi play


class GameManager:
    def __init__(self):
        self.games = {}

    def get_or_create_game(self, room_name):
        if room_name not in self.games:
            print("!!!!!!!!!!!!!!!")
            self.games[room_name] = {
                'play_bar1_position': {'x': 0, 'y': 9},
                'play_bar2_position': {'x': 0, 'y': -9},
                'play_bar3_position': {'x': 9, 'y': 0},
                'play_bar4_position': {'x': -9, 'y': 0},
                'ball_position': {'x': 0, 'y': 0},
                'ball_velocity': {'x': 0.04, 'y': 0.03},
                'score_player1': 0,
                'score_player2': 0,
                'score_player3': 0,
                'score_player4': 0,
                'game_over_flag': False,
                'game_winner': 0,
                'updating_ball_position': False,
                'connected_clients_count': 0
            }
        return self.games[room_name]

    def end_game(self, room_name):
        if room_name in self.games:
            del self.games[room_name]


game_manager = GameManager()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await asyncio.sleep(1)
        # group을 미리 만들거나 특정 닉네임을 기준으로 만드는방식?
        # 그룹에 빈공간이 있는지, 특정 닉네님이 있는지 확인
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = "chat_" + self.room_name

        await (self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        ))

        await self.accept()
        self.game_state = game_manager.get_or_create_game(self.room_name)

        self.game_state['connected_clients_count'] += 1  # 클라이언트 수 증가
        print("connected clients :" +
              str(self.game_state['connected_clients_count']))

        # print("connected clients :" + self.game_state['connected_clients_count'])
        self.player_number = self.game_state['connected_clients_count']

        if self.game_state['connected_clients_count'] == 4:
            await asyncio.sleep(3)  # 클라이언트가 2개 연결된 후 3초 기다립니다.
            if not self.game_state['updating_ball_position']:
                self.game_state['updating_ball_position'] = True
                asyncio.create_task(self.ball_position_updater())

        if self.game_state['connected_clients_count'] >= 5:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Game is full. You cannot join this game."
            }))
            self.game_state['connected_clients_count'] -= 1
            await asyncio.sleep(3)
            await self.close()

    async def disconnect(self, close_code):
        self.game_state['connected_clients_count'] -= 1

        if self.game_state['connected_clients_count'] >= 3:
            print("QQQQQQQQQQQQn")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_over_message",
                    "message": "The other player has left. The game is over."
                })

        # if self.game_state['connected_clients_count'] == 0:
        self.game_state['connected_clients_count'] = 0
        game_manager.end_game(self.room_name)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # self.game_state['connected_clients_count'] -= 1
        # if self.game_state['connected_clients_count'] == 0:
        #     game_manager.end_game(self.room_name)
        # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # print(message, " ", self.channel_name)

        if self.player_number == 1:
            if message == 'a':
                self.game_state['play_bar1_position']['x'] = max(
                    -8, self.game_state['play_bar1_position']['x'] - 0.4)
            elif message == 'd':
                self.game_state['play_bar1_position']['x'] = min(
                    9, self.game_state['play_bar1_position']['x'] + 0.4)

        if self.player_number == 2:
            if message == 'a':
                self.game_state['play_bar2_position']['x'] = max(
                    -9, self.game_state['play_bar2_position']['x'] - 0.4)
            elif message == 'd':
                self.game_state['play_bar2_position']['x'] = min(
                    8, self.game_state['play_bar2_position']['x'] + 0.4)

        if self.player_number == 3:
            if message == 'a':
                self.game_state['play_bar4_position']['y'] = max(
                    -8, self.game_state['play_bar4_position']['y'] - 0.4)
            elif message == 'd':
                self.game_state['play_bar4_position']['y'] = min(
                    9, self.game_state['play_bar4_position']['y'] + 0.4)

        if self.player_number == 4:
            if message == 'a':
                self.game_state['play_bar3_position']['y'] = max(
                    -9, self.game_state['play_bar3_position']['y'] - 0.4)
            elif message == 'd':
                self.game_state['play_bar3_position']['y'] = min(
                    8, self.game_state['play_bar3_position']['y'] + 0.4)

        # pass
        # self._update_ball_position()

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
            await asyncio.sleep(3)

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

        # 왼쪽 또는 오른쪽 벽과의 충돌
        # if self.game_state['ball_position']['x'] <= -10 or self.game_state['ball_position']['x'] >= 10:
        #     self.game_state['ball_velocity']['x'] *= -1  # x 방향 반전

        # 게임 종료 조건 확인
        # if self.game_state['score_player1'] >= self.game_state.get('game_over_score', 5) or self.game_state['score_player2'] >= self.game_state.get('game_over_score', 5):
        #     self.game_state['game_over_flag'] = True
        #     self.game_state['game_winner'] = 1 if self.game_state['score_player1'] >= self.game_state.get(
        #         'game_over_score', 5) else 2

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

        # 게임 상태 업데이트를 모든 클라이언트에 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_state': self.game_state
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
        self.game_state['ball_velocity'] = {'x': 0.04, 'y': 0.03}
        self.game_state['score_player1'] = 0
        self.game_state['score_player2'] = 0
        self.game_state['score_player3'] = 0
        self.game_state['score_player4'] = 0

        game_manager.end_game(self.room_name)

    async def game_update(self, event):
        # 이 메서드는 group_send 호출로 인해 자동으로 실행됩니다.
        await self.send(text_data=json.dumps({
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
        }))

    async def game_over_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'message': event['message']
        }))
