import re


class Checking_the_data:
    def checking_the_data(self, date, time):
        pattern1 = r'(19|20)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])'
        pattern2 = r'(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])'

        match1 = re.fullmatch(pattern1, date)
        match2 = re.fullmatch(pattern2, time)

        if match1 is None or match2 is None or not self.checking_the_date(date):
            return False

        return True

    def checking_the_date(self, date):
        '''args = date.split("-", maxsplit=3)
        year = args[0]
        month = args[1]
        day = args[2].strip()'''

        year, month, day = map(int, date.split("-"))

        if month in (1,3,5,7,8,10,12) and day <= 31:
            return True

        elif month in (4,6,9,11) and day <=30:
            return True

        elif (month == 2 and day <= 28) or (year%4==0 and year%100!=0 and month == 2 and day <= 29):
            return True

        else:
            return False