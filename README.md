# httpcannon.py #

Quickly make http requests and display the server status code, has an option to loop over the url list as many times as you want. Has support to log to Splunk port listener on non-200s. 

requires fake-useragent : https://pypi.python.org/pypi/fake-useragent 

#### Background ####
I once needed a way to test a lot of urls very quickly to verify if our apps were up and responding. I first tried using a custom bash based script but once the list grew to over 500 urls it became very slow. After a lot of googling and trail and error I found a POC using Queues and Threads. Modified it to meet our needs and this is that script. I think this was my first python script.


#### Sample urlfile.txt ####
<pre><code>
https://stackoverflow.com,/,StackOverflow_HP
https://www.google.com,/,Google_HP
https://github.com,/,GitHub_HP
https://www.amazon.com,/,Amazon_HP
https://www.cars.com,/not-real/,Cars.com_301
</code></pre>


#### Example: ####
<pre><code>
MAC1984:httpcannon kaddyman$ ./http-cannon.py -f urllist.txt

[301] FAILED Cars.com_301
urllist.txt has been processed 1/1


1 failed url tests out of 5
</code></pre>

#### Author: Ken Addyman ####
