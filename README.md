# httpcannon.py V2 #

Quickly make http requests and display the server status code, has an option to loop over the url list as many times as you want. 

Use requirements.txt to install any requirements that are not standard.  
`pip3 install -r requirements.txt`

#### Background ####
I once needed a way to test a lot of urls very quickly to verify if our apps were up and responding. I first tried using a custom bash based script but once the list grew to over 500 urls it became very slow. After a lot of googling and trail and error I found a POC using Queues and Threads. Modified it to meet our needs and this is that script. I think this was my first python2 script. I have since rewritten it in python3 and fixed some bugs the orignal had. Before the script would report false postives, that seems to be fixed now. I also simplified the url file format, no longer need to seperate out the path from the url.   

#### Sample urllist.txt ####
<pre><code>
https://stackoverflow.com/,StackOverflow_HP
https://www.google.com/,Google_HP
https://github.com/,GitHub_HP
https://www.amazon.com/,Amazon_HP
https://www.cars.com/not-real/,Cars.com_301
https://www.spotify.com/us/,Spotify_HomePage
https://www.reddit.com/,Reddit_HomePage
https://www.gjfdkljdfsklaoogle.com/fdsa/search?q=self_secceded&oq=self_secceded&aqs=chrome..69i57j0l4.98j0j4&sourceid=chrome&ie=UTF-8,WillBreak-NODOMAIN
https://www.google.com/fdsa/search?q=self_secceded&oq=self_secceded&aqs=chrome..69i57j0l4.98j0j4&sourceid=chrome&ie=UTF-8,WillBreak-404
</code></pre>


#### Example: ####

This will process the url file once, if you add the flag `--fileloop <num>` it will loop over it that many times.  

<pre><code>
ch-nb-3276:httpcannon kaddyman$ ./httpcannon.py --filename urllist.txt

[XXX] EXP_FAILED WillBreak-NODOMAIN https://www.gjfdkljdfsklaoogle.com/fdsa/search?q=self_secceded&oq=self_secceded&aqs=chrome..69i57j0l4.98j0j4&sourceid=chrome&ie=UTF-8
[200] SUCCESS StackOverflow_HP
[404] FAILED WillBreak-404
[200] SUCCESS Spotify_HomePage
[200] SUCCESS GitHub_HP
[301] FAILED Cars.com_301
[200] SUCCESS Google_HP
[200] SUCCESS Amazon_HP
[200] SUCCESS Reddit_HomePage

7 of 9 succeeded
Failed on 3
Processed url file 1

</code></pre>

#### Author: Ken Addyman ####
