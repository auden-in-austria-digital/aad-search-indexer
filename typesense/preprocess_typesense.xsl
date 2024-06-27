<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="#all" version="2.0">

    
    <xsl:template match="/">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="node()|@*">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="tei:del"/>
    <xsl:template match="tei:pb"/>
    <xsl:template match="tei:fw"/>
    <xsl:template match="tei:ab"/>

    <xsl:template match="tei:div[@type='transcription' or @xml:id='transcription']">
        <xsl:copy>
            <xsl:choose>
                <xsl:when test="ancestor::tei:text[@type='letter']">
                    <xsl:for-each-group select="./tei:div[@type]/*|./tei:div[@type]/tei:div[@type]/*" group-starting-with="tei:pb">
                        <xsl:variable name="positionOrNot" select="if(current-group()/self::tei:pb/@ed) then(current-group()/self::tei:pb/@ed) else(position())"/>
                        <div type="page" ed="{$positionOrNot}" facs="{current-group()/self::tei:pb/@facs}">
                            <xsl:choose>
                                <xsl:when test="current-group()[self::tei:div[@type='letter_message']| self::tei:div[@type='poem']| self::tei:div[@type='speech']| self::tei:div[@type='prose_translation']| self::tei:div[@type='comments']]">
                                    <xsl:for-each select="current-group()[self::tei:div|
                                                                          self::tei:lg[preceding-sibling::tei:pb]|
                                                                          self::tei:ab[preceding-sibling::tei:pb]|
                                                                          self::tei:fw]">
                                        <xsl:choose>
                                            <xsl:when test="self::tei:ab|self::tei:lg">
                                                <xsl:call-template name="text-window">
                                                    <xsl:with-param name="group">
                                                        <xsl:value-of select="'secondary'"/>
                                                    </xsl:with-param>
                                                </xsl:call-template>
                                            </xsl:when>
                                            <xsl:when test="self::tei:div[@type='poem']|self::tei:div[@type='speech']">
                                                <xsl:call-template name="text-window">
                                                    <xsl:with-param name="group">
                                                        <xsl:value-of select="'poem'"/>
                                                    </xsl:with-param>
                                                </xsl:call-template>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:call-template name="text-window">
                                                    <xsl:with-param name="group">
                                                        <xsl:value-of select="'main'"/>
                                                    </xsl:with-param>
                                                </xsl:call-template>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:for-each>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:for-each select="current-group()[self::tei:div[not(@type)]|
                                                                      self::tei:p|
                                                                      self::tei:closer|
                                                                      self::tei:lg|
                                                                      self::tei:ab|
                                                                      self::tei:fw]">
                                        <xsl:call-template name="text-window">
                                            <xsl:with-param name="group">
                                                <xsl:value-of select="'secondary'"/>
                                            </xsl:with-param>
                                        </xsl:call-template>
                                    </xsl:for-each>
                                </xsl:otherwise>
                            </xsl:choose>
                        </div>
                    </xsl:for-each-group>
                </xsl:when>
                <xsl:when test="ancestor::tei:text[@type='prose']">
                    <xsl:for-each-group select="*|./tei:div/*|//tei:floatingText/tei:body/tei:div/*" group-starting-with="tei:pb">
                        <xsl:variable name="positionOrNot" select="if(current-group()/self::tei:pb/@ed) then(current-group()/self::tei:pb/@ed) else(position())"/>
                        <div type="page" ed="{$positionOrNot}" facs="{current-group()/self::tei:pb/@facs}">
                            <xsl:choose>
                                <xsl:when test="current-group()[self::tei:div]">
            
                                    <xsl:for-each select="current-group()[self::tei:div|
                                                                        self::tei:p[preceding-sibling::tei:pb]|
                                                                        self::tei:fw[preceding-sibling::tei:pb]|
                                                                        self::tei:ab[preceding-sibling::tei:pb]]">
                                        <xsl:choose>
                                            <xsl:when test="self::tei:div">
                                                <xsl:call-template name="text-window">
                                                    <xsl:with-param name="group">
                                                        <xsl:value-of select="'main'"/>
                                                    </xsl:with-param>
                                                </xsl:call-template>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:call-template name="text-window">
                                                    <xsl:with-param name="group">
                                                        <xsl:value-of select="'secondary'"/>
                                                    </xsl:with-param>
                                                </xsl:call-template>
                                            </xsl:otherwise>
                                        </xsl:choose>
            
                                    </xsl:for-each>
                                </xsl:when>
                                <xsl:when test="current-group()[ancestor::tei:floatingText]">
                                    <xsl:for-each select="current-group()[self::tei:p|self::tei:fw|self::tei:ab|self::tei:head|self::tei:quote]">
                                        <xsl:call-template name="text-window">
                                            <xsl:with-param name="group">
                                                <xsl:value-of select="'secondary'"/>
                                            </xsl:with-param>
                                        </xsl:call-template>
                                    </xsl:for-each>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:for-each select="current-group()[self::tei:p|
                                                                self::tei:lg|
                                                                self::tei:ab|
                                                                self::tei:head|
                                                                self::tei:fw|
                                                                self::tei:quote]">
                                        <xsl:choose>
                                            <xsl:when test="self::tei:quote">
                                                <xsl:call-template name="text-window">
                                                    <xsl:with-param name="group">
                                                        <xsl:value-of select="'main'"/>
                                                    </xsl:with-param>
                                                </xsl:call-template>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:call-template name="text-window">
                                                    <xsl:with-param name="group">
                                                        <xsl:value-of select="'secondary'"/>
                                                    </xsl:with-param>
                                                </xsl:call-template>
                                            </xsl:otherwise>
                                        </xsl:choose>
            
                                    </xsl:for-each>
                                </xsl:otherwise>
                            </xsl:choose>
                        </div>
                    </xsl:for-each-group>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:for-each-group select="*" group-starting-with="tei:pb">
                        <xsl:variable name="positionOrNot" select="if(current-group()/self::tei:pb/@ed) then(current-group()/self::tei:pb/@ed) else(position())"/>
                        <div type="page" ed="{$positionOrNot}" facs="{current-group()/self::tei:pb/@facs}">
                            <xsl:for-each select="current-group()[self::tei:lg|
                                                    self::tei:p|
                                                    self::tei:fw|
                                                    self::tei:ab]">
                                <xsl:call-template name="text-window">
                                    <xsl:with-param name="group">
                                        <xsl:value-of select="'secondary'"/>
                                    </xsl:with-param>
                                </xsl:call-template>
                            </xsl:for-each>
                        </div>
                    </xsl:for-each-group>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>


    <xsl:template name="text-window">
        <xsl:param name="group"/>
        <xsl:choose>
            <xsl:when test="$group = 'secondary'">
                <xsl:copy>
                    <xsl:apply-templates select="node()|@* except (tei:lg[preceding-sibling::tei:pb] | 
                                                                tei:ab[preceding-sibling::tei:pb] | 
                                                                tei:p[preceding-sibling::tei:pb] |
                                                                tei:quote[preceding-sibling::tei:pb] |
                                                                tei:fw[preceding-sibling::tei:fw])"/>
                </xsl:copy>
            </xsl:when>
            <xsl:when test="$group = 'main'">
                <xsl:copy>
                    <xsl:apply-templates select="node()|@* except (tei:lg[preceding-sibling::tei:pb] | 
                        tei:ab[preceding-sibling::tei:pb] | 
                        tei:p[preceding-sibling::tei:pb] |
                        tei:quote[preceding-sibling::tei:pb] |
                        tei:fw[preceding-sibling::tei:fw])"/>
                </xsl:copy>
            </xsl:when>
            <xsl:when test="$group = 'poem'">
                <xsl:copy>
                    <xsl:apply-templates select="node()|@* except (tei:lg[preceding-sibling::tei:pb] | 
                        tei:ab[preceding-sibling::tei:pb] | 
                        tei:p[preceding-sibling::tei:pb] |
                        tei:quote[preceding-sibling::tei:pb] |
                        tei:fw[preceding-sibling::tei:fw])"/>
                </xsl:copy>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="tei:p[@prev]">
        <xsl:choose>
            <xsl:when test="parent::tei:div[@type='letter_message']/preceding-sibling::tei:div[@type='letter_message']">
                <xsl:copy>
                    <xsl:apply-templates select="node()|@*"/>
                </xsl:copy>
            </xsl:when>
            <xsl:when test="parent::tei:div[@type='prose']/preceding-sibling::tei:div[@type='prose']">
                <xsl:copy>
                    <xsl:apply-templates select="node()|@*"/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                <!-- do not render handled in view-type.xsl -->
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="tei:p[preceding-sibling::tei:p[@prev]]">
        <xsl:choose>
            <xsl:when test="parent::tei:div[@type='letter_message']/preceding-sibling::tei:div[@type='letter_message']">
                <xsl:copy>
                    <xsl:apply-templates select="node()|@*"/>
                </xsl:copy>
            </xsl:when>
            <xsl:when test="parent::tei:div[@type='prose']/preceding-sibling::tei:div[@type='prose']">
                <xsl:copy>
                    <xsl:apply-templates select="node()|@*"/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                <!-- do not render handled in view-type.xsl -->
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="tei:closer[not(preceding-sibling::tei:p[@prev])]">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="tei:closer[preceding-sibling::tei:p[@prev]]">
        <xsl:choose>
            <xsl:when test="parent::tei:div[@type='letter_message']/preceding-sibling::tei:div[@type='letter_message']">
                <xsl:copy>
                    <xsl:apply-templates select="node()|@*"/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                <!-- do not render handled in view-type.xsl -->
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>