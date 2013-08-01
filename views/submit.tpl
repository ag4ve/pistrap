<html>
    <head><title>PiStrap Web Interface</title></head>
    <body>
        <h1>PiStrap Web Interface</h1>
        <p>This interface can be used to manually kick of daily builds.</p>
        <p> Builds go to /var/www/build/pistrap_[suite]_[arch]_[ISO date corresponding to build]_[HH:MM].img . Images are 1000MB in size, with a 64MB boot partition</p>
        <p> You will get the path to this build, and the command that was run to generate it, if it is successful. A log is written to /var/log/pistrap.log.</p>
        <p>In the image, you will find that a minimal working system is installed and a USB serial console and ssh is set up, for headless use. There is also a minor overclock applied. Just use it as an up-to-date blank canvas to install what you need.</p>
        <p>
        <form name='build' action='http://localhost:8080/build' method='post'>
            <fieldset>
                <legend>Build Options:</legend>
                <label for='arch'>
                Please choose a processor architecture. Valid options are 'armel' and 'armhf' [Reccomended!]:
                </label> 
                <input name='arch' type='text' value='armhf'/><br/>
                <label for='dist'>    
                Please choose a software distribution. Valid options are 'debian' and 'raspbian' [Reccomended!].<br/> For the armel processor architecture, you MUST use debian, for armhf, you MUST use raspbian: 
                </label> 
                <input name='dist' type='text'  value='raspbian'/><br/>
                <label for='suite'>
                Please choose a software suite. The only valid option currently is 'wheezy':
                </label>
                <input name='suite' type='text'  value='wheezy'/><br/>
                <label for='hostname'>
                Please choose a hostname for the device: </label>
                <input name='hostname' type='text'  value='raspberry'/><br/>
                <label for='password'>
                Please choose a root password for the device: 
                </label>
                <input name='password' type='password'  value='raspberry'/><br/>
                </fieldset>
            <h4>Just click the button below, and wait!</h4>
            <input value='Build!' type='submit' />
        </form>
        </p>
        <p>
            <table border="1">
            <tr><th>Builds</th></tr>
                %for k in builds:
                      <tr>
                        <td><a href='builds/{{k}}}'>{{k}}</a></td>
                      </tr>
                %end
            </table>
        </p>
        <p>James Bennet 2013. Pistrap is Open Source, and hosted on GitHub.</p>
    </body>
</html>
