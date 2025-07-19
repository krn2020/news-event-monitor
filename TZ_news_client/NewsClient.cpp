#include "NewsClient.h"

#include <QVBoxLayout>
#include <QPushButton>
#include <QMessageBox>
#include <QTcpSocket>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QMap>

NewsClient::NewsClient(QWidget *parent) : QWidget(parent) {
    this->setWindowTitle("📺 Новости СВО — Клиент");
    this->resize(800, 600);

    QVBoxLayout *layout = new QVBoxLayout(this);

    dateEdit = new QDateEdit(QDate::currentDate());
    dateEdit->setCalendarPopup(true);
    dateEdit->setDisplayFormat("dd.MM.yyyy");
    dateEdit->setToolTip("Текущая дата");

    layout->addWidget(new QLabel("Текущая дата:"));
    layout->addWidget(dateEdit);

    searchEdit = new QLineEdit();
    searchEdit->setPlaceholderText("🔍 Поиск (например: белгород атака)");
    connect(searchEdit, &QLineEdit::textChanged, this, &NewsClient::filterEvents);
    layout->addWidget(searchEdit);

    QPushButton *btnFetch = new QPushButton("🔄 Загрузить события");
    connect(btnFetch, &QPushButton::clicked, this, &NewsClient::fetchEvents);
    layout->addWidget(btnFetch);

    QPushButton *btnStats = new QPushButton("📊 Статистика по заголовкам");
    connect(btnStats, &QPushButton::clicked, this, &NewsClient::showStatistics);
    layout->addWidget(btnStats);

    resultLabel = new QLabel("Всего событий: 0");
    layout->addWidget(resultLabel);

    browser = new QTextBrowser();
    browser->setOpenExternalLinks(true);
    layout->addWidget(browser);
}

void NewsClient::fetchEvents() {
    QTcpSocket socket;
    socket.connectToHost("127.0.0.1", 9009);
    if (!socket.waitForConnected(3000)) {
        QMessageBox::critical(this, "Ошибка", "Не удалось подключиться к серверу");
        return;
    }

    QString dateStr = dateEdit->date().toString("dd.MM.yyyy");
    QByteArray payload = dateStr.toUtf8();
    socket.write(payload);
    if (!socket.waitForBytesWritten(2000)) {
        QMessageBox::critical(this, "Ошибка", "Не удалось отправить дату");
        return;
    }

    if (!socket.waitForReadyRead(5000)) {
        QMessageBox::critical(this, "Ошибка", "Нет ответа от сервера");
        return;
    }

    QByteArray raw;
    while (socket.bytesAvailable() || socket.waitForReadyRead(100)) {
        raw += socket.readAll();
    }

    QJsonParseError err;
    QJsonDocument doc = QJsonDocument::fromJson(raw, &err);
    if (err.error != QJsonParseError::NoError) {
        QMessageBox::critical(this, "Ошибка", "Ошибка парсинга JSON: " + err.errorString());
        return;
    }

    if (!doc.isArray()) {
        QMessageBox::critical(this, "Ошибка", "Ожидался массив JSON");
        return;
    }

    allEvents = doc.array();
    resultLabel->setText(QString("Всего событий: %1").arg(allEvents.size()));
    filterEvents();
}

void NewsClient::filterEvents() {
    QString query = searchEdit->text().trimmed().toLower();
    QStringList words = query.split(' ', Qt::SkipEmptyParts);

    browser->clear();
    int matchCount = 0;

    QString html;
    for (const QJsonValue &val : allEvents) {
        QJsonObject obj = val.toObject();
        QString title = obj["title"].toString();
        QString description = obj["description"].toString();
        QString category = obj["category"].toString();
        QString date = obj["date"].toString();
        QString link = obj["link"].toString();

        QString combined = QString("%1 %2 %3 %4").arg(title, description, category, date).toLower();
        bool match = std::all_of(words.begin(), words.end(), [&](const QString &w) {
            return combined.contains(w);
        });

        if (match) {
            matchCount++;
            html += QString("<p><b>🔹 %1</b> | <i>%2</i><br>%3")
                        .arg(title, date, description);
            if (!link.isEmpty())
                html += QString("<br><a href='%1' style='color:blue'>🔗 Ссылка на новость</a>").arg(link);
            html += "</p><hr>";
        }
    }

    resultLabel->setText(QString("Всего событий: %1 | Найдено: %2").arg(allEvents.size()).arg(matchCount));

    if (html.isEmpty()) {
        browser->setHtml("<p><i>Ничего не найдено</i></p>");
    } else {
        browser->setHtml(html);
    }
}

void NewsClient::showStatistics() {
    if (allEvents.isEmpty()) {
        QMessageBox::information(this, "Статистика", "Нет загруженных событий.");
        return;
    }

    QMap<QString, int> counter;
    for (const QJsonValue &val : allEvents) {
        QString title = val.toObject()["title"].toString();
        if (!title.isEmpty())
            counter[title]++;
    }

    QStringList lines;
    for (auto it = counter.constBegin(); it != counter.constEnd(); ++it) {
        lines << QString("🔹 %1 — %2 раз(а)").arg(it.key()).arg(it.value());
    }

    QMessageBox::information(this, "Статистика по заголовкам", lines.join("\n"));
}
