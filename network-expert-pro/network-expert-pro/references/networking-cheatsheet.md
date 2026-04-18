# Aide-mémoire Réseau Expert

## 1. Ports Standards & Protocoles
- **22** : SSH (Sécurité)
- **53** : DNS (Résolution de noms)
- **80/443** : HTTP/HTTPS (Web)
- **161** : SNMP (Supervision)
- **179** : BGP (Routage)
- **500/4500** : IPsec VPN
- **3389** : RDP (Accès distant)

## 2. Table CIDR (Aide au calcul)
- `/24` : 255.255.255.0 (254 hôtes)
- `/25` : 255.255.255.128 (126 hôtes)
- `/26` : 255.255.255.192 (62 hôtes)
- `/30` : 255.255.255.252 (2 hôtes - Point à Point)

## 3. Commandes de Diagnostic (Windows/Linux)
- `tracert` / `traceroute` : Identification des sauts (hops).
- `nslookup` / `dig` : Test de la résolution DNS.
- `netstat -ano` : Visualisation des ports ouverts et connexions actives.
- `ipconfig /all` / `ip addr` : Configuration des interfaces.