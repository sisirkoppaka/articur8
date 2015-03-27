articur8
========

articur8 is an open source news clustering engine. Techmeme for the free soul, and very much amenable to hacking. :)

Here's how it looks on a mobile and a desktop (screenshots will be updated in time)

![articur8 on mobile](/images/articurate_mobile.png)

![articur8 on desktop](/images/articur8_screenshot_desktop.png)

'fab kickstart' starts the engine (corresponding interpretations for 'fab kickrestart and fab kickstop').

You'll need to run redis-server separately (assuming you have redis installed). articur8 uses it as a db.

Celery is used to distribute the performance across multicore processors. 

The view above is from a node app called 'motherlode'. To view the results, head to articurate/motherlode and run ./prereq.sh to install prerequisite modules for Motherlode.

Then ./run.sh to start the backend...it will start listening, so move to a new terminal window. The view should be available on your localhost address in browser.

This is a WIP, so the instructions/code needs cleaning up. Think Google News/Techmeme for your desktop. :) 

The current feed source is the leaderboard at Techmeme. Not too hard to switch it out in the crawler section (feed digger at articurate/fd (lb.opml file). 

