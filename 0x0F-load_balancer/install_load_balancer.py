#!/usr/bin/env bash
# install load balancer


echo -e "Updating and doing some minor checks...\n"

function install() {
	command -v "$1" &> /dev/null

	#shellcheck disable=SC2181
	if [ $? -ne 0 ]; then
		echo -e "	Installing: $1\n"
		sudo apt-get update -y -qq && \
			sudo apt-get install -y "$1" -qq
		echo -e "\n"
	else
		echo -e "	${1} is already installed.\n"
	fi
}

install haproxy #install haproxy

echo -e "\nSetting up haproxy configurations\n"

# backup default server config file
sudo cp /etc/haproxy/haproxy.cfg haproxy_default.backup

server_config\
"
defaults
  mode http
  timeout client 15s
  timeout connect 10s
  timeout server 15s
  timeout http-request 10s

frontend -frontend
    bind *:80
    bind :443 ssl crt /etc/haproxy/certs/
    http-request redirect scheme https unless { ssl_fc }
    default_backend -backend

backend -backend
    balance roundrobin
    server 310828-web-01 100.25.130.107 check
    server 310828-web-02 54.236.56.163 check

"\
# shellcheck disable=SC2154
echo "$server_config" | sudo dd status=none of=/etc/haproxy/haproxy.cfg

# enable haproxy to be started by init script
echo "ENABLED=1" | sudo dd status=none of=/etc/default/haproxy

echo "configured - Roundrobin On web-01 & web-02"

if [ "$(pgrep -c haproxy)" -le 0 ]; then
	sudo service haproxy start
else
	sudo service haproxy restart
fi
