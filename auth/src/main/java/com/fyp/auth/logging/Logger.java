package com.fyp.auth.logging;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

public class Logger {
    public static void log(String content) {
        RestTemplate restTemplate = new RestTemplate();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> requestEntity = new HttpEntity<>(content, headers);

        ResponseEntity<String> responseEntity = restTemplate
                .postForEntity("http://localhost:8081/log", requestEntity, String.class);

        if (responseEntity.getStatusCode().is2xxSuccessful()) {
            System.out.println("Successfully Logged: " + content);
        } else {
            System.out.println("Error Logging: " + content);
        }
    }
}
