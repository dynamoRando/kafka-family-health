# Data model


```mermaid
erDiagram
    FAMILY ||--|{ FAMILY_MEMBER : "has many"
    DOCTOR ||--|{ CLAIM : "is part of a"
    CLAIM }|--|{ FAMILY_MEMBER : "has many"
    CLAIM }o--|{ PAYMENT : "may have a"
    PAYMENT }o--|{ FAMILY_MEMBER: "is made by a"
    FAMILY {
        int id
        string family_name
    }
    FAMILY_MEMBER {
        int id 
        int family_id
        string name
    }
    DOCTOR {
        int id
        string name
    }
    CLAIM {
        int id
        int doctor_id
        string visit_date
        int family_member_id
        int amount
    }
    PAYMENT {
        int id
        int family_member_id
        int claim_id
        int amount
        string payment_date
    }
```