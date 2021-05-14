del /f ParticleSystemAddon.zip
cd ..
tar.exe  --exclude=*.zip  --exclude=ParticleSystemAddon/.git/* --exclude=ParticleSystemAddon/__pycache__/* -a -c -f ParticleSystemAddon.zip ParticleSystemAddon/*
move ParticleSystemAddon.zip ParticleSystemAddon/