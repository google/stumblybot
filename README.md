# StumblyBot

This is a very hacky test project to integrate Marty Robot, Google Assistant SDK
and DialogFlow.

**This is not an officially supported Google product.**

# What's inside

* Marty Router
  * Accepts long-standing connections from the robot.
  * Handles queries from DialogFlow and forwards them to the connected robot.
* Marty Server
  * Installed on a Raspberry Pi that is connected to the same WiFi network as
    Marty itself.
  * TODO: It would be awesome to use 4-wire connector to connect
    Raspberry Pi directly to the Marty controller without WiFi.
* DialogFlow configuration
  * It will understand voice queries from Google Assistant and call Marty Router
    with a webhook mechanism.

# How to make it work

* Build and deploy Router
  * Install Bazel
  * Run `bazel build ...`
  * Upload compiled binary (from `bazel-bin` directory) to a machine accessible
    from Internet.
  * Run some webserver that will accept https and proxy it to the Marty router.
  * Obtain a valid https certificate.
  * Make sure https port is available from Internet, and port 1109 (for
    connections from Marty) is available from your network.
  * TODO: Make the router serve https itself without a reverse proxy.
  * TODO: Add some encryption and authentication.
* Setup the robot
  * Install Marty python library
  * Set Marty's own IP address in `executor.py` and router address in
    `marty_server.py`.
  * TODO: Make everything properly configurable.
* Setup DialogFlow
  * Edit `agent.json`: set hostname of the server that runs your "router"
    server.
  * Archive contents of `dialogflow` directory to a zip file, so that
    `agent.json` is in the root directory of the archive.
  * Create a new project on DialogFlow.
  * Use "Restore from zip" to upload the configuration.
  * Configure Assistant to invoke your test project.

# How to debug it

* Make sure robot server is able to connect to the Marty controller. The server
  writes some debugging information on stdout on startup.
* Make sure robot server is able to connect to the router. Both robot and router
  write debugging information on stdout.
* Make sure https endpoint is accessible from internet.
  `https://<your_router>/apiai` should say something.
* Make sure your agent is available from DialogFlow debugging console (on the
  right hand side).
* Make sure your agent can be activated with a command from Assistant devices.

# Assistant SDK

You can install Assistant SDK on the same Raspberry Pi, connect speaker and
microphone to it, and it will act as regular Google Assistant. This step is
optional. You can use any Assistant-enabled device to control your robot. Google
Home, Android, iOS, smart TV, whatever.

# Contacts

https://groups.google.com/forum/#!forum/stumblybot - project discussion group.
