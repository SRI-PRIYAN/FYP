package com.fyp.auth.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "users")
@AllArgsConstructor
@NoArgsConstructor
public @Data class User {
    @Id
    private String username;
    private String password;
}
