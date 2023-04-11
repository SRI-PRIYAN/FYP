package com.fyp.auth.controller;

import com.fyp.auth.logging.Logger;
import com.fyp.auth.model.User;
import com.fyp.auth.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
public class AuthenticationController {
    @Autowired
    private UserService userService;

    @GetMapping("/register")
    public String register(Model model) {
        model.addAttribute("user", new User());
        return "register";
    }

    @GetMapping("/login")
    public String login() {
        return "login";
    }

    @PostMapping("/register")
    public String register(User user, BindingResult bindingResult, Model model) {
        if (bindingResult.hasErrors()) {
            return "register";
        }

        try {
            userService.createNewUser(user);
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
            return "register";
        }

        Logger.log(user.getUsername());

        return "redirect:/login";
    }

    @GetMapping("/logout")
    public String logout() {
        return "logout";
    }
}
