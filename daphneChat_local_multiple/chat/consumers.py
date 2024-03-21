import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    connected_clients_count = 0
    updating_ball_position = False

    game_over_flag = False
    game_winner_local = 0

    play_bar1_position = {'x': 0, 'y': 9}
    play_bar2_position = {'x': 0, 'y': -9}
    play_bar3_position = {'x': 9, 'y': 0}
    play_bar4_position = {'x': -9, 'y': 0}

    ball_position = {'x': 0, 'y': 0}
    ball_velocity = {'x': 0.06, 'y': 0.04}  # 공의 속도
    score_player1 = 0
    score_player2 = 0
    score_player3 = 0
    score_player4 = 0

    game_over_score = 3

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = "chat_" + self.room_name

        await (self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        ))
        await self.accept()
        asyncio.create_task(self.ball_position_updater())

    async def disconnect(self, close_code):
        ChatConsumer.connected_clients_count -= 1
        await (self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message, " ", self.channel_name)

        # 계산식
        if message == 'q':
            ChatConsumer.play_bar1_position['x'] = max(
                -9, ChatConsumer.play_bar1_position['x'] - 0.4)
        elif message == 'e':
            ChatConsumer.play_bar1_position['x'] = min(
                9, ChatConsumer.play_bar1_position['x'] + 0.4)
            
        if message == 'i':
            ChatConsumer.play_bar2_position['x'] = max(
                -9, ChatConsumer.play_bar2_position['x'] - 0.4)
        elif message == 'p':
            ChatConsumer.play_bar2_position['x'] = min(
                9, ChatConsumer.play_bar2_position['x'] + 0.4)
            
        if message == 'z':
            ChatConsumer.play_bar4_position['y'] = max(
                -9, ChatConsumer.play_bar4_position['y'] - 0.4)
        elif message == 'c':
            ChatConsumer.play_bar4_position['y'] = min(
                9, ChatConsumer.play_bar4_position['y'] + 0.4)
            
        if message == 'b':
            ChatConsumer.play_bar3_position['y'] = max(
                -9, ChatConsumer.play_bar3_position['y'] - 0.4)
        elif message == 'm':
            ChatConsumer.play_bar3_position['y'] = min(
                9, ChatConsumer.play_bar3_position['y'] + 0.4)

    async def _update_ball_position(self):
        # 공 위치 업데이트
        ChatConsumer.ball_position['x'] += ChatConsumer.ball_velocity['x']
        ChatConsumer.ball_position['y'] += ChatConsumer.ball_velocity['y']

        bar_width = 2  # 예시 값, 실제 바의 가로 길이에 맞게 조정
        ball_radius = 0.5  # 예시 값, 실제 공의 반지름에 맞게 조정

        # # 첫 번째 플레이어 바와 공의 충돌 검사
        if ChatConsumer.play_bar1_position['y'] - ball_radius < ChatConsumer.ball_position['y'] < ChatConsumer.play_bar1_position['y'] + ball_radius \
                and self.play_bar1_position['x'] - bar_width / 2 < self.ball_position['x'] < self.play_bar1_position['x'] + bar_width / 2:
            ChatConsumer.ball_velocity['y'] *= -1  # y 방향 반전

        # # 두 번째 플레이어 바와 공의 충돌 검사
        if ChatConsumer.play_bar2_position['y'] - ball_radius < ChatConsumer.ball_position['y'] < ChatConsumer.play_bar2_position['y'] + ball_radius \
                and ChatConsumer.play_bar2_position['x'] - bar_width / 2 < ChatConsumer.ball_position['x'] < ChatConsumer.play_bar2_position['x'] + bar_width / 2:
            ChatConsumer.ball_velocity['y'] *= -1  # y 방향 반전

        if ChatConsumer.play_bar3_position['x'] - ball_radius < ChatConsumer.ball_position['x'] < ChatConsumer.play_bar3_position['x'] + ball_radius \
                and ChatConsumer.play_bar3_position['y'] - bar_width / 2 < ChatConsumer.ball_position['y'] < ChatConsumer.play_bar3_position['y'] + bar_width / 2:
            ChatConsumer.ball_velocity['x'] *= -1  # y 방향 반전

        if ChatConsumer.play_bar4_position['x'] - ball_radius < ChatConsumer.ball_position['x'] < ChatConsumer.play_bar4_position['x'] + ball_radius \
                and ChatConsumer.play_bar4_position['y'] - bar_width / 2 < ChatConsumer.ball_position['y'] < ChatConsumer.play_bar4_position['y'] + bar_width / 2:
            ChatConsumer.ball_velocity['x'] *= -1  # y 방향 반전

        # 벽과의 충돌 처리
        # up ,down wall collision
        if ChatConsumer.ball_position['y'] <= -10 or ChatConsumer.ball_position['y'] >= 10:
            # collision on upper side wall, player2 score up
            if ChatConsumer.ball_position['y'] > 10:
                ChatConsumer.score_player1 += 1
            # collision on bottom side wall,player1 score up
            elif ChatConsumer.ball_position['y'] < -10:
                ChatConsumer.score_player2 += 1

            ChatConsumer.ball_position = {'x': 0, 'y': 0}
            ChatConsumer.play_bar1_position = {'x': 0, 'y': 9}
            ChatConsumer.play_bar2_position = {'x': 0, 'y': -9}
            ChatConsumer.play_bar3_position = {'x': 9, 'y': 0}
            ChatConsumer.play_bar4_position = {'x': -9, 'y': 0}
            await asyncio.sleep(2)

        if ChatConsumer.ball_position['x'] <= -10 or ChatConsumer.ball_position['x'] >= 10:
            # collision on upper side wall, player2 score up
            if ChatConsumer.ball_position['x'] > 10:
                ChatConsumer.score_player4 += 1
            # collision on bottom side wall,player1 score up
            elif ChatConsumer.ball_position['x'] < -10:
                ChatConsumer.score_player3 += 1

            ChatConsumer.ball_position = {'x': 0, 'y': 0}
            ChatConsumer.play_bar1_position = {'x': 0, 'y': 9}
            ChatConsumer.play_bar2_position = {'x': 0, 'y': -9}
            ChatConsumer.play_bar3_position = {'x': 9, 'y': 0}
            ChatConsumer.play_bar4_position = {'x': -9, 'y': 0}
            await asyncio.sleep(2)
        
            # 실점 후 판 재배치

        if ChatConsumer.score_player1 == ChatConsumer.game_over_score:
            ChatConsumer.game_over_flag = True
            ChatConsumer.game_winner_local = 1

        if ChatConsumer.score_player2 == ChatConsumer.game_over_score:
            ChatConsumer.game_over_flag = True
            ChatConsumer.game_winner_local = 2

        if ChatConsumer.score_player3 == ChatConsumer.game_over_score:
            ChatConsumer.game_over_flag = True
            ChatConsumer.game_winner_local = 3

        if ChatConsumer.score_player4 == ChatConsumer.game_over_score:
            ChatConsumer.game_over_flag = True
            ChatConsumer.game_winner_local = 4

        # left, right wall collisio
        # if ChatConsumer.ball_position['x'] <= -10 or ChatConsumer.ball_position['x'] >= 10:
        #     ChatConsumer.ball_velocity['x'] *= -1  # x 방향 반전

        # 모든 클라이언트에 변경된 정보 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',  # 호출할 메서드 이름
                'play_bar1_position': ChatConsumer.play_bar1_position,
                'play_bar2_position': ChatConsumer.play_bar2_position,
                'play_bar3_position': ChatConsumer.play_bar3_position,
                'play_bar4_position': ChatConsumer.play_bar4_position,
                'ball_position': ChatConsumer.ball_position,
                'score_player1': ChatConsumer.score_player1,
                'score_player2': ChatConsumer.score_player2,
                'score_player3': ChatConsumer.score_player3,
                'score_player4': ChatConsumer.score_player4,
                'game_over_flag': ChatConsumer.game_over_flag,
                'game_winner': ChatConsumer.game_winner_local
            }
        )

    async def ball_position_updater(self):

        while not ChatConsumer.game_over_flag:
            await self._update_ball_position()
            await asyncio.sleep(0.02)  # 50번의 업데이트가 1초 동안 진행됨

        ChatConsumer.game_over_flag = False
        ChatConsumer.connected_clients_count = 0
        ChatConsumer.updating_ball_position = False
        ChatConsumer.game_over_flag = False
        ChatConsumer.game_winner_local = 0
        ChatConsumer.play_bar1_position = {'x': 0, 'y': 9}
        ChatConsumer.play_bar2_position = {'x': 0, 'y': -9}
        ChatConsumer.play_bar3_position = {'x': -9, 'y': 0}
        ChatConsumer.play_bar4_position = {'x': 9, 'y': 0}
        ChatConsumer.ball_position = {'x': 0, 'y': 0}
        ChatConsumer.ball_velocity = {'x': 0.03, 'y': 0.02}  # 공의 속도
        ChatConsumer.score_player1 = 0
        ChatConsumer.score_player2 = 0
        ChatConsumer.score_player3 = 0
        ChatConsumer.score_player4 = 0
        ChatConsumer.game_over_score = 3

    async def game_update(self, event):
        # 이 메서드는 group_send 호출로 인해 자동으로 실행됩니다.
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
