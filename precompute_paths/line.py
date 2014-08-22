class Line:
    def __init__(self, json):
        self.id = json['id']
        self.x1 = json['x1']
        self.y1 = json['y1']
        self.x2 = json['x2']
        self.y2 = json['y2']
