#ifndef NEWSCLIENT_H
#define NEWSCLIENT_H

#include <QWidget>
#include <QDateEdit>
#include <QLineEdit>
#include <QTextBrowser>
#include <QLabel>
#include <QJsonArray>

class NewsClient : public QWidget {
    Q_OBJECT

public:
    explicit NewsClient(QWidget *parent = nullptr);

private slots:
    void fetchEvents();
    void filterEvents();
    void showStatistics();

private:
    QDateEdit *dateEdit;
    QLineEdit *searchEdit;
    QTextBrowser *browser;
    QLabel *resultLabel;
    QJsonArray allEvents;
};

#endif // NEWSCLIENT_H
