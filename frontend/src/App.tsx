import { useState, useEffect } from 'react';
import './App.css';
import { getFriends } from './util/APIClient';
import ListItem from './components/ListItem';
import { FriendActivity } from './util/types';

function App() {
	const [friends, setFriends] = useState<Array<FriendActivity>>([]);

    useEffect(() => {
        getFriends().then(friends => setFriends(friends));
    }, []);

    return (
        <div className="App">
			<h1>Friend Activity</h1>
			<div className="friend-list-wrapper">
				{friends.map((friend, index) => (
					<ListItem key={index} {...friend} />
				))}
			</div>
        </div>
    );
}

export default App;
