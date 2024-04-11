import LoginModal from "./views/LoginModal.js";
import FA2Modal from "./views/FA2Modal.js";
import Off2 from "./views/games/Off2View.js";
import OffTour from "./views/games/OffTourView.js";
import On2 from "./views/games/On2View.js";
import On4 from "./views/games/On4View.js";
import GameSelectView from "./views/GameSelectView.js";
import GameEnterView from "./views/GameEnterView.js";

let currentView = null;

document.addEventListener('DOMContentLoaded', async () => {
    initializeRouting();
    window.onpopstate = routePage; 
   	await routePage(); 

    let access_token = localStorage.getItem('access_token');
	let access_token_expire_time = Number(localStorage.getItem('expire_time'));
	let current_time = Math.floor(Date.now() / 1000);
	
	if (access_token_expire_time != 0 && access_token_expire_time <= current_time) localStorage.clear();
    
    if (!access_token || !localStorage.getItem('FA2_verified')) {
        let security_code = getCodeFromUrl();

        if (!security_code) {
            LoginModal.displayLoginModal();
        } else if (!access_token) {
            await fetchAccessToken(security_code);
            access_token = localStorage.getItem('access_token'); 
            const emailAndCode = await getEmailAndCode(access_token);
          	await FA2Modal.displayFA2Modal(emailAndCode, access_token); 
        } else {
            const emailAndCode = await getEmailAndCode(access_token);
			await FA2Modal.displayFA2Modal(emailAndCode, access_token); 
        }
    }
});

function navigate(path) {
	console.log("currentView", currentView);
	if (currentView && typeof currentView.cleanup === 'function') {
        currentView.cleanup();
		history.replaceState(null, null, path);
    } else {
		history.pushState(null, null, path);

	}
    routePage();
}

function initializeRouting() {
    document.addEventListener('click', e => {
        if (e.target.matches('[data-link]')) {
            e.preventDefault();
            navigate(e.target.href);
        }
    });
}

async function routePage() {
    const routes = [
        { path: "/", view: GameEnterView },
        { path: "/game/select", view: GameSelectView },
        { path: "/game/off/2", view: Off2 },
        { path: "/game/off/tour", view: OffTour },
        { path: "/game/on/2", view: On2 },
        { path: "/game/on/4", view: On4 }
    ];

    const potentialMatches = routes.map(route => {
        return {
            route: route,
            isMatch: location.pathname === route.path
        };
    });

    let match = potentialMatches.find(potentialMatch => potentialMatch.isMatch);

    if (!match) {
        match = { route: "/", view: GameEnterView }; 
        history.pushState(null, null, "/");
    }

    const view = new match.route.view({ navigate });
    if (currentView && typeof currentView.cleanup === 'function') {
        currentView.cleanup();
    }
    currentView = view;

	document.querySelector("#app").innerHTML = await view.getHtml();

	if (view.addEventListeners && typeof view.addEventListeners === 'function') {
        view.addEventListeners();
    }

	if (view.initialize && typeof view.initialize === 'function') {
        await view.initialize();
    }
}

function getCodeFromUrl() {
    const security_code = new URLSearchParams(window.location.search).get('code');
	if (security_code) {
		history.replaceState(null, '', window.location.pathname);
		routePage();
	}
    return security_code
}

async function getEmailAndCode(access_token) { 
    try {
		console.log(`the access token when calling email = ${access_token}`);
        const response = await fetch('/get/userinfo', {
            method: 'get',
            headers: {
                'Authorization': 'Bearer ' + access_token
            }
        });
        const data = await response.json(); 
        return data; 
    } catch (error) {
        console.error('Error fetching user info', error);
    }
}

async function fetchAccessToken(code) { 
    try {
		console.log("code = ", code);
        const response = await fetch('/get/security', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code })
        });
        const data = await response.json();
		console.log("data = ", data);

        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
			localStorage.setItem('expire_time', Math.floor(Date.now() / 1000) + data.expires_in);
        } else {
            console.log('Failed to obtain access token.');
        }
    } catch (error) {
        console.error('Error fetching access token:', error);
    }
}