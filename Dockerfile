FROM powerapi/powerapi:0.6

WORKDIR /opt/rapl_formula
USER powerapi

COPY --chown=powerapi . /opt/rapl_formula/rapl_formula
RUN pip3 install --user --no-cache-dir -e "/opt/rapl_formula/rapl_formula"

ENTRYPOINT ["python3", "-m", "rapl_formula"]
