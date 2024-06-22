# Listen Along

## About

A simple web app to that allows you to listen to your friends on Spotify. This works for all your followed users who share their spotify activity. You just need to supply it with your `sp_dc` cookie from your browser which should last a year.

![](img/listen-along-screenshot.png)

## How to run

1. Clone the repository

```bash
git clone https://github.com/Fidasek009/listen-along.git
```

2. Find your `sp_dc` cookie at https://open.spotify.com/

![](img/sp_dc-cookie.png)

3. Create a `.env` file containing your cookie

```bash
cd listen-along
echo 'SP_DC_COOKIE="<your cookie>"' > .env
```

4. Run the app

```bash
docker-compose up -d
```
