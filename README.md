how to launch

1. reinstall venv
git clone (clone_name)

cd pongpongBack

rm -rf myprojectvenv

python3 -m venv myprojectvenv

2. activate venv
. myprojectvenv/bin/activate

3. install modules
pip install -r requirements.txt
(maybe error occured)

4. launch server
cd WebService

daphne -e ssl:8000:privateKey=/home/ubuntu/pongpongBack/myprojectenv/lib/python3.10/site-packages/sslserver/certs/development.key:certKey=/home/ubuntu/pongpongBack/myprojectenv/lib/python3.10/site-packages/sslserver/certs/development.crt WebService.asgi:application