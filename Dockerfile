FROM ubuntu:latest
RUN apt-get update && apt-get install -y \
    texlive \
    texlive-latex-base \
    texlive-lang-cyrillic \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    imagemagick \
    coreutils \
    vim \
    sudo \
    python3-pip \
    openssh-server
#Configure ssh
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN mkdir /var/run/sshd
RUN bash -c 'install -m755 <(printf "#!/bin/sh\nexit 0") /usr/sbin/policy-rc.d'
RUN ex +'%s/^#\zeListenAddress/\1/g' -scwq /etc/ssh/sshd_config
RUN ex +'%s/^#\zeHostKey .*ssh_host_.*_key/\1/g' -scwq /etc/ssh/sshd_config
RUN RUNLEVEL=1 dpkg-reconfigure openssh-server
RUN ssh-keygen -A -v
RUN update-rc.d ssh defaults
RUN echo 'root:SecRetPaSSwOrD' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
RUN ssh-keygen -t rsa -P "droopy" -f ~/.ssh/id_rsa
RUN cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
#Configure web app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
#Comment PASSW_ADMIN to get random admin's pass
ENV PASSW_ADMIN=r04S9[.Wb6
EXPOSE 5022
CMD ["/bin/bash", "-c", "/usr/sbin/sshd && flask run --host=0.0.0.0"]