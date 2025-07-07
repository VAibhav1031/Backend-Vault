# Flask Blog Website

A simple Flask-based blog website that can be accessed online through Cloudflare Tunnel.

## About

This is a Flask web application that serves as a blog website. The site is hosted locally on a laptop but made accessible worldwide using Cloudflare Tunnel.

## How It Works

- The Flask app runs on a local server (laptop)
- Cloudflare Tunnel forwards traffic from the domain `necromancer-blog.xyz` to the local server
- The tunnel routes requests to the specific port where the Flask app is running
- This allows the locally hosted app to be accessible from anywhere on the internet

## Availability

The website is accessible at `necromancer-blog.xyz` when:
- The local server is running
- The Cloudflare Tunnel is active
- The Flask application is started
- second if i want to (cause i hosted this on my laptop/ good for your small scale project)

## Setup for Similar Projects

This approach works well for small-scale projects where you want to:
- Host applications locally
- Make them accessible online
- Use an affordable domain name
- Avoid expensive hosting costs

## Requirements

- Flask application
- Cloudflare Tunnel (cloudflared) (for linux it is mostly available in official repo or you can clone the repo and make it )
- Domain name (buy any good universal cheap domain, best for the project mann)
- Local server/computer to run the application 

## Usage

1. Start your Flask application locally
2. Start the Cloudflare Tunnel
3. Your website will be accessible through your domain/ you can buy some cheap  good domain service(check renewal also)

Note: The website availability depends on keeping both the tunnel and server running (can use systemd, or tmux  for linux user).
