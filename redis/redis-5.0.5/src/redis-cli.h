typedef struct migrating_slot {
    int flag;
    unsigned int slot;
    char* source_ip;
    int source_port;
    char* target_ip;
    int target_port;             
} migrating_slot;
extern migrating_slot pairs;
