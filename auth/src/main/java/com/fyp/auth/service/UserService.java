package com.fyp.auth.service;

import com.fyp.auth.model.User;
import com.fyp.auth.repository.UserRepository;
import lombok.AllArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class UserService {
    private UserRepository userRepository;
    private PasswordEncoder passwordEncoder;

    public void createNewUser(User user) throws Exception {
        if (userRepository.findByUsername(user.getUsername()) != null) {
            throw new Exception("Username Already Exists!");
        }

        user.setPassword(passwordEncoder.encode(user.getPassword()));

        userRepository.save(user);
    }
}
