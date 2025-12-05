-- VPN Launcher AppleScript Application
-- Manages both udp2raw and WireGuard connections

property udp2rawPID : 0
property wireguardActive : false
property configPath : ""
property userName : ""

on run
	-- Get the username from config file
	set configPath to (path to application support from user domain as text) & "CapybaraVPN:config.txt"

	try
		set configFile to read file configPath
		set userName to paragraph 1 of configFile
	on error
		display dialog "VPN not configured. Please reinstall." buttons {"OK"} default button 1 with icon stop
		return
	end try

	showMainMenu()
end run

on showMainMenu()
	set dialogText to "Capybara VPN Manager" & return & return & "User: " & userName & return & "Status: "

	if isVPNRunning() then
		set dialogText to dialogText & "Connected"
		set buttonsList to {"Disconnect", "Quit"}
		set defaultBtn to "Disconnect"
	else
		set dialogText to dialogText & "Disconnected"
		set buttonsList to {"Connect", "Quit"}
		set defaultBtn to "Connect"
	end if

	set userChoice to button returned of (display dialog dialogText buttons buttonsList default button defaultBtn with icon note)

	if userChoice is "Connect" then
		connectVPN()
	else if userChoice is "Disconnect" then
		disconnectVPN()
	else if userChoice is "Quit" then
		if isVPNRunning() then
			display dialog "VPN is still running. Disconnect first?" buttons {"Cancel", "Disconnect & Quit"} default button 2
			if button returned of result is "Disconnect & Quit" then
				disconnectVPN()
			end if
		end if
		return
	end if

	-- Show menu again
	showMainMenu()
end showMainMenu

on connectVPN()
	try
		-- Start udp2raw
		display notification "Starting udp2raw tunnel..." with title "Capybara VPN"

		set udp2rawScript to "sudo /usr/local/bin/udp2raw -c -l 127.0.0.1:4096 -r 66.42.119.38:443 -k SecureVPN2025Obfuscate --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 > /tmp/udp2raw.log 2>&1 &"

		do shell script udp2rawScript with administrator privileges
		delay 2

		-- Start WireGuard
		display notification "Starting WireGuard..." with title "Capybara VPN"

		set wgConfigPath to (path to application support from user domain as text) & "CapybaraVPN:" & userName & "_wireguard.conf"
		set wgConfigPosix to POSIX path of wgConfigPath

		do shell script "sudo /usr/local/bin/wg-quick up " & quoted form of wgConfigPosix with administrator privileges

		delay 1

		-- Verify connection
		try
			set vpnIP to do shell script "ping -c 1 -W 2 10.7.0.1 2>&1"
			display notification "Connected successfully!" with title "Capybara VPN" sound name "Glass"
		on error
			display dialog "VPN started but connection test failed. Check your settings." buttons {"OK"} default button 1 with icon caution
		end try

	on error errMsg
		display dialog "Failed to connect: " & errMsg buttons {"OK"} default button 1 with icon stop
	end try
end connectVPN

on disconnectVPN()
	try
		display notification "Disconnecting VPN..." with title "Capybara VPN"

		-- Stop WireGuard
		set wgConfigPath to (path to application support from user domain as text) & "CapybaraVPN:" & userName & "_wireguard.conf"
		set wgConfigPosix to POSIX path of wgConfigPath

		try
			do shell script "sudo /usr/local/bin/wg-quick down " & quoted form of wgConfigPosix with administrator privileges
		end try

		-- Stop udp2raw
		try
			do shell script "sudo killall udp2raw" with administrator privileges
		end try

		delay 1
		display notification "Disconnected" with title "Capybara VPN" sound name "Glass"

	on error errMsg
		display dialog "Error disconnecting: " & errMsg buttons {"OK"} default button 1 with icon caution
	end try
end disconnectVPN

on isVPNRunning()
	try
		set udp2rawRunning to (do shell script "pgrep udp2raw 2>/dev/null || echo ''")
		set wgRunning to (do shell script "pgrep wg-quick 2>/dev/null || echo ''")

		if udp2rawRunning is not "" or wgRunning is not "" then
			return true
		else
			return false
		end if
	on error
		return false
	end try
end isVPNRunning
