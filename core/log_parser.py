import re
from datetime import datetime

class LogParser:
    @staticmethod
    def parse_log_content(content: str):
        """
        Recebe todo o conteúdo de um arquivo de log (string) e gera uma lista de entradas.
        """
        log_entries = []
        for line in content.split('\n'):
            if line.strip():
                entry = LogParser.parse_log_line(line)
                if entry:
                    log_entries.append(entry)
        return log_entries

    @staticmethod
    def parse_log_line(line: str):
        """
        Tenta fazer match com os padrões de log. 
        Retorna um dicionário com as informações da linha ou None se não bater nos padrões.
        """
        # Padrão 1
        pattern1 = re.match(
            r'\[(?P<worker>Worker-[^\]]+)\] \[(?P<timestamp>[^\]]+)\] (?P<level>\w+) (?P<task>\[[^\]]+\])? ?(?P<message>.*)',
            line
        )
        # Padrão 2
        pattern2 = re.match(
            r'\[(?P<timestamp>[\d\-:, ]+)\] (?P<level>\w+) \[(?P<worker>[^\]]+)\](?P<message>.*)',
            line
        )

        if pattern1:
            entry = pattern1.groupdict()
        elif pattern2:
            entry = pattern2.groupdict()
        else:
            return None

        # Converte timestamp para horário local, se possível
        entry['timestamp'] = LogParser.convert_to_local_time(entry['timestamp'])
        entry['full_message'] = line
        return entry

    @staticmethod
    def convert_to_local_time(timestamp: str) -> str:
        """
        Converte 'YYYY-MM-DD HH:MM:SS,mmm' para o horário local (se possível).
        """
        try:
            utc_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
            local_time = utc_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
            return local_time
        except ValueError:
            # Se não for nesse formato, retorna como está
            return timestamp