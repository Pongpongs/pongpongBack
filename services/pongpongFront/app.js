const express = require('express');
const https = require('https');
const querystring = require('querystring');
const path = require('path');
const app = express();
const nodemailer = require('nodemailer');
const port = 3000;
const fs = require('fs');
const fetch = require('node-fetch');
const jwt = require('jsonwebtoken');
const webpack = require('webpack');

require('dotenv').config();

module.exports = {
    entry: './frontend/static/js/index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'bundle.js'
    },
    plugins: [
        new webpack.DefinePlugin({
            'CLIENT_ID_FOR_F': JSON.stringify(process.env.CLIENT_ID),
        }),
    ],
    // Additional configurations such as loaders, resolve options, etc.
};

const privateKeyPath = process.env.PRIVATE_KEY_PATH;
const certificatePath = process.env.CERTIFICATE_PATH;

const privateKey = fs.readFileSync(privateKeyPath, 'utf8');
const certificate = fs.readFileSync(certificatePath, 'utf8');


const agent = new https.Agent({
    key: privateKey,
    cert: certificate,
    rejectUnauthorized: false
});

app.use(express.json());
app.use(express.static(path.resolve(__dirname, 'frontend')));

app.get('/', (req, res) => {
    res.sendFile(path.resolve("frontend", "index.html"));
});

app.get('/game/*', (req, res) => {
	res.sendFile(path.resolve("frontend", "index.html"));
});

app.post('/backend/send', async (req, res) => {
    // const realBackendURL = 'https://pongpongback.duckdns.org/realback/send';
    const realBackendURL = 'https://pongpongstest.duckdns.org/b/realback/send';
	
	const jwt_secret_key = process.env.JWT_KEY;
    const { userEmail, access_token } = req.body;

	const jwt_token = jwt.sign({
		user_email: userEmail,
		access_token: access_token
	},
	jwt_secret_key,
	{expiresIn: '1h'});

	
    try {
        const response = await fetch(realBackendURL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${jwt_token}`
            },
			agent: agent
        });
		
        if (response.status == 200 || response.status == 201) {
            res.status(200).send();
        } else {
            throw new Error('Failed to forward request to real backend server.');
        }	
    } catch (error) {
        console.error('Error forwarding request:', error);
        res.status(500).send('Error forwarding request to real backend server.');
    }
});

app.get('/get/security', (req, res) => {
    const code = req.query.code;
    if (code) {
        res.redirect(`https://pongpongstest.duckdns.org/?code=${code}`);
    } else {
        res.status(400).send("Code not given");
    }
});

app.post('/get/security', (req, res) => {
    const code = req.body.code;

	
    const postData = querystring.stringify({
        grant_type: 'authorization_code',
        client_id: process.env.CLIENT_ID,
        client_secret: process.env.CLIENT_SECRET,
        code: code,
        redirect_uri: process.env.REDIRECT_URI
    });

    const options = {
        hostname: 'api.intra.42.fr',
        path: '/oauth/token',
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    };
	  
    const request = https.request(options, response => {
        let data = '';
        response.on('data', chunk => {
            data += chunk;
        });
        response.on('end', () => {
            res.json(JSON.parse(data));
			
        });
    });

    request.on('error', error => {
        console.error('Error requesting access token:', error);
        res.status(500).send('Failed to obtain access token');
    });

    request.write(postData);
    request.end();
});

app.get('/get/userinfo', (req, res) => {
    const access_token = req.headers.authorization;
    
    const getUserInfo = () => {
        return new Promise((resolve, reject) => {
            const options = {
                hostname: 'api.intra.42.fr',
                path: '/v2/me',
                method: 'GET',
                headers: {
                    'Authorization': access_token
                }
            };

            const request = https.request(options, response => {
                let data = '';
                response.on('data', chunk => {
                    data += chunk;
                });
                response.on('end', () => {
                    resolve(data); 
                });
            });

            request.on('error', error => {
                reject(error); 
            });

            request.end();
        });
    };

    
    const sendEmail = async (userEmail, verificationCode) => {
        let transporter = nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: process.env.MY_EMAIL,
                pass: process.env.PASS
            }
        });

        let mailOptions = {
            from: process.env.MY_EMAIL,
            to: userEmail,
            subject: 'Pongpongstest 2FA Code',
            text: `Your Verification Code: ${verificationCode}`
        };

        try {
            let info = await transporter.sendMail(mailOptions);
            
        } catch (error) {
            console.error('Error sending email:', error);
        }
    };

    
    (async () => {
        try {
            const data = await getUserInfo();
            const parsedData = JSON.parse(data); 
            const userEmail = parsedData.email;

            const verificationCode = Math.floor(100000 + Math.random() * 900000);
            await sendEmail(userEmail, verificationCode); 
            res.json({email: userEmail, code: verificationCode});
        } catch (error) {
            console.error('Error:', error);
            res.status(500).send('An error occurred');
        }
    })();
});

app.listen(port, () => {
    
});
